import secrets

from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

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
    

    @staticmethod
    def send_reset_email(user, token):
        reset_url = (
          f"{settings.FRONTEND_URL}"
          f"/reset-password/"
          f"?token={token.token}"
    )

        context = {
          "user": user,
          "reset_url": reset_url,
    }

        html_body = render_to_string(
          "accounts/emails/password_reset.html",
          context,
    )

        email = EmailMultiAlternatives(
           subject="Password Reset Request",
           body="Reset your password using the link.",
           from_email=settings.DEFAULT_FROM_EMAIL,
           to=[user.email],
    )

        email.attach_alternative(
           html_body,
          "text/html",
    )

        email.send(fail_silently=False)

