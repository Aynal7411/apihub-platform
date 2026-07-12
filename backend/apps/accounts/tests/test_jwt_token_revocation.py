from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken


User = get_user_model()


class JWTTokenRevocationTestCase(APITestCase):
    """
    Sprint 3.2.7.8
    JWT Token Revocation & Session Management

    Tests:
    1. Authenticated user can logout.
    2. Logout requires authentication.
    3. Logout requires a refresh token.
    4. Logout blacklists the supplied refresh token.
    5. A revoked refresh token cannot be reused.
    6. Logout does not revoke unrelated refresh tokens.
    7. Invalid refresh tokens are rejected.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username="revocation_user",
            email="revocation@example.com",
            password="StrongPassword123!",
        )

        self.logout_url = reverse("accounts:logout")
        self.refresh_url = reverse("accounts:token-refresh")

        # Create first JWT session.
        self.refresh_token = RefreshToken.for_user(self.user)
        self.access_token = self.refresh_token.access_token

        self.refresh_token_string = str(self.refresh_token)
        self.access_token_string = str(self.access_token)

    def authenticate(self, access_token=None):
        """
        Add JWT access token to the Authorization header.
        """
        token = access_token or self.access_token_string

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )

    def test_authenticated_user_can_logout(self):
        """
        A valid authenticated user should be able to logout
        using a valid refresh token.
        """
        self.authenticate()

        response = self.client.post(
            self.logout_url,
            {
                "refresh": self.refresh_token_string,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn("success", response.data)
        self.assertTrue(response.data["success"])

    def test_logout_requires_authentication(self):
        """
        Logout endpoint must reject unauthenticated requests.
        """
        response = self.client.post(
            self.logout_url,
            {
                "refresh": self.refresh_token_string,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_logout_requires_refresh_token(self):
        """
        Authenticated logout request without a refresh token
        must be rejected.
        """
        self.authenticate()

        response = self.client.post(
            self.logout_url,
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_logout_blacklists_refresh_token(self):
        """
        Successful logout must blacklist the supplied
        refresh token.
        """
        self.authenticate()

        response = self.client.post(
            self.logout_url,
            {
                "refresh": self.refresh_token_string,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertTrue(
            BlacklistedToken.objects.filter(
                token__jti=self.refresh_token["jti"]
            ).exists()
        )

    def test_revoked_refresh_token_cannot_be_reused(self):
        """
        Once a refresh token is blacklisted during logout,
        it must not be usable to obtain new tokens.
        """
        self.authenticate()

        logout_response = self.client.post(
            self.logout_url,
            {
                "refresh": self.refresh_token_string,
            },
            format="json",
        )

        self.assertEqual(
            logout_response.status_code,
            status.HTTP_200_OK,
        )

        # Remove Authorization header because refresh
        # endpoint should not require an access token.
        self.client.credentials()

        refresh_response = self.client.post(
            self.refresh_url,
            {
                "refresh": self.refresh_token_string,
            },
            format="json",
        )

        self.assertEqual(
            refresh_response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_logout_does_not_revoke_other_refresh_tokens(self):
        """
        Single-session logout must revoke only the supplied
        refresh token, not another active refresh token.
        """
        second_refresh = RefreshToken.for_user(self.user)

        self.authenticate()

        response = self.client.post(
            self.logout_url,
            {
                "refresh": self.refresh_token_string,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertTrue(
            BlacklistedToken.objects.filter(
                token__jti=self.refresh_token["jti"]
            ).exists()
        )

        self.assertFalse(
            BlacklistedToken.objects.filter(
                token__jti=second_refresh["jti"]
            ).exists()
        )

    def test_invalid_refresh_token_is_rejected(self):
        """
        Invalid refresh tokens must not result
        in a successful logout.
        """
        self.authenticate()

        response = self.client.post(
            self.logout_url,
            {
                "refresh": "invalid-refresh-token",
            },
            format="json",
        )

        self.assertIn(
            response.status_code,
            [
                status.HTTP_400_BAD_REQUEST,
                status.HTTP_401_UNAUTHORIZED,
            ],
        )

        self.assertNotEqual(
            response.status_code,
            status.HTTP_200_OK,
        )