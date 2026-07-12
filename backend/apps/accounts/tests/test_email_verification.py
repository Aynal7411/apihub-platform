from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import override_settings
from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase

from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import EmailVerificationToken
from apps.accounts.services.email_verification_service import (
    EmailVerificationService,
)


User = get_user_model()


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    EMAIL_VERIFICATION_RESEND_COOLDOWN_SECONDS=60,
)
class EmailVerificationTestCase(APITestCase):
    """
    Production-grade integration tests for:

    - valid email verification
    - invalid tokens
    - expired tokens
    - single-use tokens
    - authentication requirements
    - resend cooldown
    - verified-user protection
    - token rotation
    - email delivery
    """

    def setUp(self):
        self.password = "StrongPassword123!"

        self.user = User.objects.create_user(
            email="verification@example.com",
            username="verification-user",
            password=self.password,
            is_email_verified=False,
        )

        self.verify_url = reverse(
            "accounts:verify-email"
        )

        self.resend_url = reverse(
            "accounts:resend-email-verification"
        )

    # ============================================================
    # Helpers
    # ============================================================

    def authenticate(self, user=None):
        """
        Authenticate API client using a real JWT access token.
        """

        user = user or self.user

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        self.client.credentials(
            HTTP_AUTHORIZATION=(
                f"Bearer {access_token}"
            )
        )

        return access_token

    def clear_authentication(self):
        self.client.credentials()

    def create_verification_token(self, user=None):
        """
        Create a real verification token using the
        production service.

        Expected return value:
            raw_token

        If your service returns:
            (token_object, raw_token)

        adjust this helper accordingly.
        """

        user = user or self.user

        result = (
            EmailVerificationService
            .create_verification_token(
                user=user
            )
        )

        # Supports either:
        #
        # raw_token
        #
        # or:
        #
        # (token_object, raw_token)

        if isinstance(result, tuple):
            return result[-1]

        return result

    def get_latest_token(self, user=None):
        user = user or self.user

        return (
            EmailVerificationToken.objects
            .filter(user=user)
            .order_by("-created_at")
            .first()
        )

    # ============================================================
    # Valid Token
    # ============================================================

    def test_valid_token_verifies_email(self):
        """
        A valid verification token must verify the user's email.
        """

        raw_token = self.create_verification_token()

        response = self.client.post(
            self.verify_url,
            {
                "token": raw_token,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.user.refresh_from_db()

        self.assertTrue(
            self.user.is_email_verified
        )

        self.assertIsNotNone(
            self.user.email_verified_at
        )

    # ============================================================
    # Invalid Token
    # ============================================================

    def test_invalid_token_is_rejected(self):
        """
        Random or malformed verification tokens must not
        verify an account.
        """

        response = self.client.post(
            self.verify_url,
            {
                "token": (
                    "invalid-email-verification-token"
                ),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.user.refresh_from_db()

        self.assertFalse(
            self.user.is_email_verified
        )

        self.assertIsNone(
            self.user.email_verified_at
        )

    # ============================================================
    # Missing Token
    # ============================================================

    def test_verification_requires_token(self):
        """
        Verification requests without a token must fail safely.
        """

        response = self.client.post(
            self.verify_url,
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.user.refresh_from_db()

        self.assertFalse(
            self.user.is_email_verified
        )

    # ============================================================
    # Expired Token
    # ============================================================

    def test_expired_token_is_rejected(self):
        """
        Expired verification tokens must not verify accounts.
        """

        raw_token = self.create_verification_token()

        token_object = self.get_latest_token()

        token_object.expires_at = (
            timezone.now()
            - timedelta(seconds=1)
        )

        token_object.save(
            update_fields=["expires_at"]
        )

        response = self.client.post(
            self.verify_url,
            {
                "token": raw_token,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.user.refresh_from_db()

        self.assertFalse(
            self.user.is_email_verified
        )

    # ============================================================
    # Single-use Token
    # ============================================================

    def test_verification_token_is_single_use(self):
        """
        A successfully consumed verification token must
        never be usable again.
        """

        raw_token = self.create_verification_token()

        first_response = self.client.post(
            self.verify_url,
            {
                "token": raw_token,
            },
            format="json",
        )

        self.assertEqual(
            first_response.status_code,
            status.HTTP_200_OK,
        )

        second_response = self.client.post(
            self.verify_url,
            {
                "token": raw_token,
            },
            format="json",
        )

        self.assertEqual(
            second_response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_successful_verification_marks_token_as_used(self):
        """
        Successful verification must persist token consumption.
        """

        raw_token = self.create_verification_token()

        token_object = self.get_latest_token()

        self.assertIsNone(
            token_object.used_at
        )

        response = self.client.post(
            self.verify_url,
            {
                "token": raw_token,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        token_object.refresh_from_db()

        self.assertIsNotNone(
            token_object.used_at
        )

    # ============================================================
    # Standard API Response
    # ============================================================

    def test_verify_email_returns_standard_response_structure(self):
        """
        Successful verification must follow the project's
        standard API response contract.
        """

        raw_token = self.create_verification_token()

        response = self.client.post(
            self.verify_url,
            {
                "token": raw_token,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn(
            "success",
            response.data,
        )

        self.assertIn(
            "message",
            response.data,
        )

        self.assertIn(
            "data",
            response.data,
        )

        self.assertTrue(
            response.data["success"]
        )

        self.assertIsInstance(
            response.data["data"],
            dict,
        )

    # ============================================================
    # Resend Authentication
    # ============================================================

    def test_resend_requires_authentication(self):
        """
        Anonymous users must not be able to trigger
        verification emails.
        """

        self.clear_authentication()

        response = self.client.post(
            self.resend_url,
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    # ============================================================
    # Unverified User Resend
    # ============================================================

    def test_unverified_authenticated_user_can_resend(self):
        """
        An authenticated unverified user should be able
        to request another verification email.
        """

        self.authenticate()

        response = self.client.post(
            self.resend_url,
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    # ============================================================
    # Verified User Protection
    # ============================================================

    def test_verified_user_cannot_request_resend(self):
        """
        Already verified users must not generate unnecessary
        verification tokens.
        """

        self.user.is_email_verified = True
        self.user.email_verified_at = timezone.now()

        self.user.save(
            update_fields=[
                "is_email_verified",
                "email_verified_at",
            ]
        )

        self.authenticate()

        response = self.client.post(
            self.resend_url,
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    # ============================================================
    # Resend Cooldown
    # ============================================================

    def test_resend_cooldown_prevents_rapid_requests(self):
        """
        Repeated resend requests within the cooldown window
        must be throttled.
        """

        self.authenticate()

        first_response = self.client.post(
            self.resend_url,
            {},
            format="json",
        )

        self.assertEqual(
            first_response.status_code,
            status.HTTP_200_OK,
        )

        second_response = self.client.post(
            self.resend_url,
            {},
            format="json",
        )

        self.assertEqual(
            second_response.status_code,
            status.HTTP_429_TOO_MANY_REQUESTS,
        )

    # ============================================================
    # Cooldown Expiration
    # ============================================================

    def test_resend_allowed_after_cooldown_expires(self):
        """
        A user should be able to resend after the cooldown
        period has elapsed.
        """

        self.authenticate()

        first_response = self.client.post(
            self.resend_url,
            {},
            format="json",
        )

        self.assertEqual(
            first_response.status_code,
            status.HTTP_200_OK,
        )

        latest_token = self.get_latest_token()

        latest_token.created_at = (
            timezone.now()
            - timedelta(seconds=61)
        )

        latest_token.save(
            update_fields=["created_at"]
        )

        second_response = self.client.post(
            self.resend_url,
            {},
            format="json",
        )

        self.assertEqual(
            second_response.status_code,
            status.HTTP_200_OK,
        )

    # ============================================================
    # Token Rotation
    # ============================================================

    def test_resend_rotates_verification_token(self):
        """
        Resending verification must create a new token and
        invalidate the previous active token.
        """

        old_raw_token = (
            self.create_verification_token()
        )

        old_token = self.get_latest_token()

        # Move outside cooldown window.
        old_token.created_at = (
            timezone.now()
            - timedelta(seconds=61)
        )

        old_token.save(
            update_fields=["created_at"]
        )

        self.authenticate()

        response = self.client.post(
            self.resend_url,
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        old_token.refresh_from_db()

        # The old token should no longer be usable.
        old_token_response = self.client.post(
            self.verify_url,
            {
                "token": old_raw_token,
            },
            format="json",
        )

        self.assertEqual(
            old_token_response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_resend_creates_new_verification_token(self):
        """
        Resend must result in a newly persisted verification
        token for the authenticated user.
        """

        self.authenticate()

        initial_count = (
            EmailVerificationToken.objects
            .filter(user=self.user)
            .count()
        )

        response = self.client.post(
            self.resend_url,
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        final_count = (
            EmailVerificationToken.objects
            .filter(user=self.user)
            .count()
        )

        self.assertGreater(
            final_count,
            initial_count,
        )

    # ============================================================
    # Email Delivery
    # ============================================================

    def test_resend_sends_verification_email(self):
        """
        Successful resend must send exactly one email.
        """

        self.authenticate()

        self.assertEqual(
            len(mail.outbox),
            0,
        )

        response = self.client.post(
            self.resend_url,
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(mail.outbox),
            1,
        )

        email = mail.outbox[0]

        self.assertIn(
            self.user.email,
            email.to,
        )

    def test_verification_email_contains_verification_link(self):
        """
        Verification email should contain a usable
        verification URL or token-based link.
        """

        self.authenticate()

        response = self.client.post(
            self.resend_url,
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(mail.outbox),
            1,
        )

        email = mail.outbox[0]

        self.assertIn(
            "verify",
            email.body.lower(),
        )

    # ============================================================
    # User Isolation
    # ============================================================

    def test_resend_creates_token_only_for_authenticated_user(self):
        """
        Resend must never create verification tokens for
        another user.
        """

        other_user = User.objects.create_user(
            email="other@example.com",
            username="other-user",
            password=self.password,
            is_email_verified=False,
        )

        self.authenticate(self.user)

        response = self.client.post(
            self.resend_url,
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertTrue(
            EmailVerificationToken.objects
            .filter(user=self.user)
            .exists()
        )

        self.assertFalse(
            EmailVerificationToken.objects
            .filter(user=other_user)
            .exists()
        )