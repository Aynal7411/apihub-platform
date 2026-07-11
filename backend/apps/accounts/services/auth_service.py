from django.db import transaction
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken
from apps.common.exceptions import InvalidCredentials


User = get_user_model()


class AuthService:

    @staticmethod
    @transaction.atomic
    def register_user(validated_data):

        

        password = validated_data.pop("password")

        user = User.objects.create_user(
            password=password,
            **validated_data,
        )

        return user


    @staticmethod
    def login(email, password):
        """
        Authenticate user and generate JWT tokens.
        """

        email = email.strip().lower()

        user = authenticate(
            email=email,
            password=password,
        )

        if user is None:
           raise InvalidCredentials()

        if not user.is_active:
            raise AuthenticationFailed(
                "User account is inactive."
            )

        refresh = RefreshToken.for_user(user)

        return {
            "user": user,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }