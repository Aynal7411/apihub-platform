from __future__ import annotations

import hashlib
import secrets
from datetime import timedelta
from typing import Final

from django.conf import settings
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from rest_framework.exceptions import Throttled
from apps.accounts.models import EmailVerificationToken


class EmailVerificationService:
    """
    Service responsible for the complete lifecycle of email verification tokens.

    Security properties:
    - Cryptographically secure random tokens
    - Only SHA-256 token hashes are stored in the database
    - Time-limited tokens
    - Single-use verification
    - Previous active tokens can be invalidated
    - Database operations are transaction-safe
    """

    DEFAULT_TOKEN_EXPIRY_MINUTES: Final[int] = 30
    TOKEN_BYTES: Final[int] = 32

    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------

    @classmethod
    def get_token_expiry_minutes(cls) -> int:
        """
        Return the configured email-verification token lifetime.

        settings.py example:
            EMAIL_VERIFICATION_TOKEN_EXPIRY_MINUTES = 30
        """
        return getattr(
            settings,
            "EMAIL_VERIFICATION_TOKEN_EXPIRY_MINUTES",
            cls.DEFAULT_TOKEN_EXPIRY_MINUTES,
        )

    # ------------------------------------------------------------------
    # Token utilities
    # ------------------------------------------------------------------

    @staticmethod
    def generate_raw_token() -> str:
        """
        Generate a cryptographically secure URL-safe token.

        The raw token must only be returned to the caller and sent
        to the user. It must never be stored directly in the database.
        """
        return secrets.token_urlsafe(
            EmailVerificationService.TOKEN_BYTES
        )

    @staticmethod
    def hash_token(raw_token: str) -> str:
        """
        Create a deterministic SHA-256 hash of a raw verification token.
        """
        if not isinstance(raw_token, str) or not raw_token.strip():
            raise ValidationError(
                {
                    "token": [
                        "A valid email verification token is required."
                    ]
                }
            )

        return hashlib.sha256(
            raw_token.encode("utf-8")
        ).hexdigest()

    # ------------------------------------------------------------------
    # Token creation
    # ------------------------------------------------------------------

    @classmethod
    @transaction.atomic
    def create_verification_token(
        cls,
        user,
        *,
        invalidate_existing: bool = True,
    ) -> str:
        """
        Create a new verification token for a user.

        Returns:
            The raw token. Only this raw value should be sent to the user.

        The database stores only its SHA-256 hash.
        """

        # Lock the user row to prevent concurrent token-generation races.
        user_model = user.__class__

        locked_user = (
            user_model.objects
            .select_for_update()
            .get(pk=user.pk)
        )

        if locked_user.is_email_verified:
            raise ValidationError(
                {
                    "email": [
                        "This email address has already been verified."
                    ]
                }
            )

        if invalidate_existing:
            cls._invalidate_existing_tokens(
                user=locked_user
            )

        raw_token = cls.generate_raw_token()
        token_hash = cls.hash_token(raw_token)

        expires_at = timezone.now() + timedelta(
            minutes=cls.get_token_expiry_minutes()
        )

        EmailVerificationToken.objects.create(
            user=locked_user,
            token_hash=token_hash,
            expires_at=expires_at,
        )

        return raw_token

    # ------------------------------------------------------------------
    # Token verification
    # ------------------------------------------------------------------

    @classmethod
    @transaction.atomic
    def verify_token(cls, raw_token: str):
        """
        Verify a raw email-verification token.

        On success:
        - Marks the token as used
        - Marks the user's email as verified
        - Sets email_verified_at
        - Invalidates remaining unused verification tokens

        Returns:
            The verified user.
        """

        token_hash = cls.hash_token(raw_token)

        try:
            verification_token = (
                EmailVerificationToken.objects
                .select_for_update()
                .select_related("user")
                .get(token_hash=token_hash)
            )
        except EmailVerificationToken.DoesNotExist:
            raise ValidationError(
                {
                    "token": [
                        "Invalid email verification token."
                    ]
                }
            )

        now = timezone.now()

        if verification_token.used_at is not None:
            raise ValidationError(
                {
                    "token": [
                        "This email verification token has already been used."
                    ]
                }
            )

        if verification_token.expires_at <= now:
            raise ValidationError(
                {
                    "token": [
                        "This email verification token has expired."
                    ]
                }
            )

        user_model = verification_token.user.__class__

        user = (
            user_model.objects
            .select_for_update()
            .get(pk=verification_token.user_id)
        )

        # Defensive idempotency for an already verified account.
        if user.is_email_verified:
            verification_token.used_at = now
            verification_token.save(
                update_fields=["used_at"]
            )

            raise ValidationError(
                {
                    "email": [
                        "This email address has already been verified."
                    ]
                }
            )

        # Consume the token.
        verification_token.used_at = now
        verification_token.save(
            update_fields=["used_at"]
        )

        # Verify the user's email.
        user.is_email_verified = True
        user.email_verified_at = now
        user.save(
            update_fields=[
                "is_email_verified",
                "email_verified_at",
            ]
        )

        # Invalidate any other outstanding verification tokens.
        (
            EmailVerificationToken.objects
            .filter(
                user=user,
                used_at__isnull=True,
            )
            .exclude(pk=verification_token.pk)
            .update(used_at=now)
        )

        return user

    # ------------------------------------------------------------------
    # Token invalidation
    # ------------------------------------------------------------------

    @staticmethod
    def _invalidate_existing_tokens(*, user) -> int:
        """
        Mark all currently unused verification tokens as used.

        Returns:
            Number of invalidated tokens.
        """
        return (
            EmailVerificationToken.objects
            .filter(
                user=user,
                used_at__isnull=True,
            )
            .update(
                used_at=timezone.now()
            )
        )

    @classmethod
    @transaction.atomic
    def invalidate_all_tokens(cls, user) -> int:
        """
        Public API for invalidating all unused email-verification tokens
        belonging to a user.
        """
        return cls._invalidate_existing_tokens(
            user=user
        )

    # ------------------------------------------------------------------
    # Maintenance helpers
    # ------------------------------------------------------------------

    @staticmethod
    def delete_expired_tokens() -> int:
        """
        Delete expired verification tokens.

        Suitable for a periodic Celery task or management command.

        Returns:
            Number of deleted database rows.
        """
        deleted_count, _ = (
            EmailVerificationToken.objects
            .filter(
                expires_at__lte=timezone.now()
            )
            .delete()
        )

        return deleted_count
    
    @staticmethod
    def enforce_resend_cooldown(user) -> None:
        cooldown_seconds = getattr(
            settings,
            "EMAIL_VERIFICATION_RESEND_COOLDOWN_SECONDS",
            60,
        )

        latest_token = (
            EmailVerificationToken.objects
            .filter(user=user)
            .order_by("-created_at")
            .first()
        )

        if latest_token is None:
            return

        next_allowed_at = (
            latest_token.created_at
            + timedelta(seconds=cooldown_seconds)
        )

        now = timezone.now()

        if now < next_allowed_at:
            wait_seconds = max(
                1,
                int(
                    (
                        next_allowed_at - now
                    ).total_seconds()
                ),
            )

            raise Throttled(
                wait=wait_seconds,
                detail=(
                    "Please wait before requesting "
                    "another verification email."
                ),
            )