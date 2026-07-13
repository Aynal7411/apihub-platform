import logging

from celery import shared_task
from django.contrib.auth import get_user_model
from apps.accounts.models import PasswordResetToken
from apps.accounts.services.verification_email_service import (
    VerificationEmailService,
)
from apps.accounts.services.password_reset_service import (
    PasswordResetService,
)

logger = logging.getLogger(__name__)

User = get_user_model()


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
    retry_kwargs={"max_retries": 3},
)
def send_verification_email_task(
    self,
    user_id: int,
    invalidate_existing: bool = True,
):
    user = User.objects.get(pk=user_id)

    VerificationEmailService.send_verification_email(
        user=user,
        invalidate_existing=invalidate_existing,
    )

    logger.info(
        "Verification email sent successfully for user_id=%s",
        user_id,
    )

    return {
        "status": "sent",
        "user_id": user_id,
    }


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
    retry_kwargs={"max_retries": 3},
)
def send_password_reset_email_task(
    self,
    user_id,
    reset_token_id,
):
    user = User.objects.get(pk=user_id)

    reset_token = PasswordResetToken.objects.get(
        pk=reset_token_id,
    )

    PasswordResetService.send_reset_email(
        user=user,
        token=reset_token,
    )

    logger.info(
        "Password reset email sent successfully for user_id=%s",
        user_id,
    )

    return {
        "status": "sent",
        "user_id": str(user_id),
    }