from django.db import transaction
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken
from apps.common.exceptions import InvalidCredentials
from rest_framework_simplejwt.exceptions import TokenError
from apps.accounts.services.token_service import TokenService
from apps.accounts.tasks import send_verification_email_task
from rest_framework_simplejwt.token_blacklist.models import (
    OutstandingToken,
    BlacklistedToken,
)

User = get_user_model()


class AuthService:

    @staticmethod
    def refresh_token(refresh_token):

        try:

            refresh = RefreshToken(
                refresh_token
            )


            access_token = refresh.access_token


            return {
                "access": str(access_token),
                "refresh": str(refresh),
            }


        except TokenError:

            raise Exception(
                "Invalid refresh token"
            )
        
    @staticmethod
    @transaction.atomic
    def register_user(validated_data):

        

        password = validated_data.pop("password")

        user = User.objects.create_user(
            password=password,
            **validated_data,
        )
        transaction.on_commit(
        lambda: send_verification_email_task.delay(user.pk)
    )
        return user


    @staticmethod
    def login(*,email, password):
        """
        Authenticate user and generate JWT tokens.
        """

        email = email.strip().lower()

        user = authenticate(
            email=email,
            password=password,
        )

        if user is None:
           raise AuthenticationFailed( "Invalid email or password.")

        if not user.is_active:
            raise AuthenticationFailed(
                "User account is inactive."
            )

        refresh = RefreshToken.for_user(user)

        tokens = TokenService.create_tokens_for_user(user)

        return {
         "user": user,
        "refresh": tokens["refresh"],
         "access": tokens["access"],
}
    
    @staticmethod
    def logout(refresh_token):
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()

        except TokenError:
            raise AuthenticationFailed(
                "Invalid or expired refresh token."
            )
        
    @staticmethod
    @transaction.atomic
    def logout_all(user):
        """
        Revoke all outstanding refresh-token sessions
        belonging to the specified user.

        Idempotent:
        already-blacklisted tokens are not duplicated.
        """

        outstanding_tokens = OutstandingToken.objects.filter(
            user=user
        )

        revoked_sessions = 0

        for token in outstanding_tokens:
            _, created = BlacklistedToken.objects.get_or_create(
                token=token
            )

            if created:
                revoked_sessions += 1

        return revoked_sessions  
    
    @staticmethod
    @transaction.atomic
    def reset_password(token, new_password):
        reset_token = (
        PasswordResetToken.objects
        .select_for_update()
        .filter(token=token)
        .first()
    )

        if not reset_token:
          return None

        if reset_token.is_used():
          return None

        if reset_token.is_expired():
          return None

        user = reset_token.user

        user.set_password(new_password)
        user.save(update_fields=["password"])

        reset_token.mark_as_used()

        return user
    
    