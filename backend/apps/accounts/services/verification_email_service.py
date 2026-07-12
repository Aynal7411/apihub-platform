from __future__ import annotations

import logging
from urllib.parse import urlencode

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from apps.accounts.services.email_verification_service import (
    EmailVerificationService,
)

logger = logging.getLogger(__name__)


class VerificationEmailService:
    """
    Handles email-verification email generation and delivery.
    """

    @staticmethod
    def build_verification_url(raw_token: str) -> str:
        frontend_url = getattr(
            settings,
            "FRONTEND_URL",
            "http://localhost:3000",
        ).rstrip("/")

        verification_path = getattr(
            settings,
            "EMAIL_VERIFICATION_FRONTEND_PATH",
            "/verify-email",
        )

        query_string = urlencode({"token": raw_token})

        return (
            f"{frontend_url}"
            f"{verification_path}"
            f"?{query_string}"
        )

    @classmethod
    def send_verification_email(
        cls,
        user,
        *,
        invalidate_existing: bool = True,
    ) -> None:
        raw_token = (
            EmailVerificationService.create_verification_token(
                user=user,
                invalidate_existing=invalidate_existing,
            )
        )

        verification_url = cls.build_verification_url(raw_token)

        context = {
            "user": user,
            "verification_url": verification_url,
            "expiry_minutes": (
                EmailVerificationService.get_token_expiry_minutes()
            ),
        }

        text_body = render_to_string(
            "accounts/emails/verify_email.txt",
            context,
        )

        html_body = render_to_string(
            "accounts/emails/verify_email.html",
            context,
        )

        email = EmailMultiAlternatives(
            subject="Verify your email address",
            body=text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )

        email.attach_alternative(
            html_body,
            "text/html",
        )

        try:
            email.send(fail_silently=False)
        except Exception:
            logger.exception(
                "Failed to send verification email for user_id=%s",
                user.pk,
            )
            raise