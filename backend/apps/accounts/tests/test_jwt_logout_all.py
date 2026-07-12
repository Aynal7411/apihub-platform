from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import (
    OutstandingToken,
    BlacklistedToken,
)


User = get_user_model()


class JWTLogoutAllDevicesTestCase(APITestCase):
    """
    Sprint 3.2.7.9
    JWT Logout All Devices & Advanced Session Revocation.

    Security guarantees tested:
    - Authentication is required.
    - All refresh-token sessions belonging to the authenticated user
      can be revoked.
    - Another user's sessions are not affected.
    - Revoked refresh tokens cannot be reused.
    - Already-blacklisted tokens are handled safely.
    - Repeated logout-all requests are safe and idempotent.
    - API responses follow the standardized response structure.
    """

    def setUp(self):
        self.logout_all_url = reverse("accounts:logout-all")
        self.refresh_url = reverse("accounts:token-refresh")

        self.user = User.objects.create_user(
            username="logout_all_user",
            email="logoutall@example.com",
            password="StrongPassword123!",
        )

        self.other_user = User.objects.create_user(
            username="other_user",
            email="other@example.com",
            password="StrongPassword123!",
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def create_token_pair(self, user):
        """
        Create a fresh JWT refresh/access token pair for a user.
        """
        refresh = RefreshToken.for_user(user)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

    def authenticate(self, access_token):
        """
        Authenticate subsequent API requests using an access token.
        """
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {access_token}"
        )

    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------

    def test_logout_all_requires_authentication(self):
        """
        Anonymous users must not be able to revoke sessions.
        """
        response = self.client.post(
            self.logout_all_url,
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    # ------------------------------------------------------------------
    # Successful logout-all
    # ------------------------------------------------------------------

    def test_authenticated_user_can_logout_from_all_devices(self):
        """
        An authenticated user should be able to request
        account-wide refresh-token revocation.
        """
        token_pair = self.create_token_pair(self.user)

        self.authenticate(token_pair["access"])

        response = self.client.post(
            self.logout_all_url,
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertTrue(response.data["success"])

    # ------------------------------------------------------------------
    # Revoke every session owned by current user
    # ------------------------------------------------------------------

    def test_logout_all_blacklists_all_user_refresh_tokens(self):
        """
        Every outstanding refresh token belonging to the authenticated
        user must be blacklisted.
        """
        session_one = self.create_token_pair(self.user)
        session_two = self.create_token_pair(self.user)
        session_three = self.create_token_pair(self.user)

        self.authenticate(session_one["access"])

        response = self.client.post(
            self.logout_all_url,
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        outstanding_tokens = OutstandingToken.objects.filter(
            user=self.user
        )

        self.assertGreaterEqual(
            outstanding_tokens.count(),
            3,
        )

        for token in outstanding_tokens:
            self.assertTrue(
                BlacklistedToken.objects.filter(
                    token=token
                ).exists(),
                msg=(
                    f"Outstanding token with JTI {token.jti} "
                    "was not blacklisted."
                ),
            )

    # ------------------------------------------------------------------
    # User isolation
    # ------------------------------------------------------------------

    def test_logout_all_does_not_revoke_other_users_tokens(self):
        """
        Account-wide logout must affect only the authenticated user.
        """
        user_session = self.create_token_pair(self.user)
        other_user_session = self.create_token_pair(self.other_user)

        self.authenticate(user_session["access"])

        response = self.client.post(
            self.logout_all_url,
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        other_user_tokens = OutstandingToken.objects.filter(
            user=self.other_user
        )

        self.assertTrue(other_user_tokens.exists())

        for token in other_user_tokens:
            self.assertFalse(
                BlacklistedToken.objects.filter(
                    token=token
                ).exists(),
                msg="Another user's refresh token was incorrectly revoked.",
            )

        # Other user's refresh token should still work.
        refresh_response = self.client.post(
            self.refresh_url,
            {
                "refresh": other_user_session["refresh"],
            },
            format="json",
        )

        self.assertEqual(
            refresh_response.status_code,
            status.HTTP_200_OK,
        )

    # ------------------------------------------------------------------
    # Revoked tokens cannot be reused
    # ------------------------------------------------------------------

    def test_revoked_refresh_tokens_cannot_be_reused(self):
        """
        Refresh tokens revoked through logout-all must no longer
        generate new access tokens.
        """
        session_one = self.create_token_pair(self.user)
        session_two = self.create_token_pair(self.user)

        self.authenticate(session_one["access"])

        logout_response = self.client.post(
            self.logout_all_url,
            {},
            format="json",
        )

        self.assertEqual(
            logout_response.status_code,
            status.HTTP_200_OK,
        )

        # Clear authentication because the refresh endpoint is public.
        self.client.credentials()

        for refresh_token in (
            session_one["refresh"],
            session_two["refresh"],
        ):
            response = self.client.post(
                self.refresh_url,
                {
                    "refresh": refresh_token,
                },
                format="json",
            )

            self.assertIn(
                response.status_code,
                (
                    status.HTTP_401_UNAUTHORIZED,
                    status.HTTP_400_BAD_REQUEST,
                ),
            )

    # ------------------------------------------------------------------
    # Already revoked token handling
    # ------------------------------------------------------------------

    def test_logout_all_handles_already_blacklisted_tokens(self):
        """
        Logout-all must not fail when one or more user refresh tokens
        have already been blacklisted.
        """
        first_session = self.create_token_pair(self.user)
        second_session = self.create_token_pair(self.user)

        # Revoke one token before logout-all.
        RefreshToken(
            first_session["refresh"]
        ).blacklist()

        self.authenticate(second_session["access"])

        response = self.client.post(
            self.logout_all_url,
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        outstanding_tokens = OutstandingToken.objects.filter(
            user=self.user
        )

        for token in outstanding_tokens:
            self.assertTrue(
                BlacklistedToken.objects.filter(
                    token=token
                ).exists()
            )

    # ------------------------------------------------------------------
    # Idempotency
    # ------------------------------------------------------------------

    def test_logout_all_is_idempotent(self):
        """
        Repeated logout-all operations should not create duplicate
        blacklist records or produce server errors.

        A fresh access token is used for the second request because
        SimpleJWT blacklist revokes refresh tokens, not already-issued
        access tokens.
        """
        session = self.create_token_pair(self.user)

        self.authenticate(session["access"])

        first_response = self.client.post(
            self.logout_all_url,
            {},
            format="json",
        )

        self.assertEqual(
            first_response.status_code,
            status.HTTP_200_OK,
        )

        blacklist_count_after_first_request = (
            BlacklistedToken.objects.filter(
                token__user=self.user
            ).count()
        )

        second_response = self.client.post(
            self.logout_all_url,
            {},
            format="json",
        )

        self.assertEqual(
            second_response.status_code,
            status.HTTP_200_OK,
        )

        blacklist_count_after_second_request = (
            BlacklistedToken.objects.filter(
                token__user=self.user
            ).count()
        )

        self.assertEqual(
            blacklist_count_after_first_request,
            blacklist_count_after_second_request,
        )

    # ------------------------------------------------------------------
    # Standardized API response
    # ------------------------------------------------------------------

    def test_logout_all_returns_standard_response_structure(self):
        """
        Successful logout-all responses must follow the project's
        standardized API response contract.
        """
        session = self.create_token_pair(self.user)

        self.authenticate(session["access"])

        response = self.client.post(
            self.logout_all_url,
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn("success", response.data)
        self.assertIn("message", response.data)
        self.assertIn("data", response.data)

        self.assertTrue(response.data["success"])

        self.assertEqual(
            response.data["message"],
            "Logged out from all devices successfully.",
        )

        self.assertIsInstance(
            response.data["data"],
            dict,
        )

        self.assertIn(
            "revoked_sessions",
            response.data["data"],
        )