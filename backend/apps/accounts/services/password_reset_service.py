import secrets

from datetime import timedelta

from django.utils import timezone

from apps.accounts.models import PasswordResetToken


class PasswordResetService:
    """
    Handles password reset token generation
    and validation.
    """


    TOKEN_EXPIRY_MINUTES = 30


    @staticmethod
    def create_token(user):

        # invalidate previous active tokens
        PasswordResetToken.objects.filter(
            user=user,
            used_at__isnull=True
        ).update(
            used_at=timezone.now()
        )


        token = secrets.token_urlsafe(48)


        reset_token = PasswordResetToken.objects.create(
            user=user,
            token=token,
            expires_at=(
                timezone.now()
                +
                timedelta(
                    minutes=
                    PasswordResetService.TOKEN_EXPIRY_MINUTES
                )
            )
        )


        return reset_token



    @staticmethod
    def validate_token(token):

        reset_token = (
            PasswordResetToken.objects
            .filter(
                token=token
            )
            .first()
        )


        if not reset_token:
            return None


        if reset_token.is_used():
            return None


        if reset_token.is_expired():
            return None


        return reset_token