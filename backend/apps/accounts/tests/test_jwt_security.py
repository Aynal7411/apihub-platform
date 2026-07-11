from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework_simplejwt.exceptions import TokenError


User = get_user_model()


class JWTSecurityTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="jwtsecurity@example.com",
            username="jwtsecurity",
            password="StrongPassword123!",
        )

        self.me_url = reverse("accounts:me")

        self.refresh = RefreshToken.for_user(self.user)
        self.access = self.refresh.access_token

    def test_access_token_type_is_correct(self):
        """
        Access token must contain token_type=access.
        """
        self.assertEqual(
            self.access["token_type"],
            "access",
        )

    def test_refresh_token_type_is_correct(self):
        """
        Refresh token must contain token_type=refresh.
        """
        self.assertEqual(
            self.refresh["token_type"],
            "refresh",
        )

    def test_access_token_lifetime_configuration(self):
        """
        Access token lifetime must match SIMPLE_JWT configuration.
        """
        token_lifetime = (
            self.access["exp"] - self.access["iat"]
        )

        expected_lifetime = int(
            settings.SIMPLE_JWT[
                "ACCESS_TOKEN_LIFETIME"
            ].total_seconds()
        )

        self.assertEqual(
            token_lifetime,
            expected_lifetime,
        )

    def test_access_token_lifetime_configuration(self):
        """
        Access token lifetime should approximately match
        SIMPLE_JWT configuration.
        """
        token_lifetime = self.access["exp"] - self.access["iat"]

        expected_lifetime = int(
        settings.SIMPLE_JWT[
            "ACCESS_TOKEN_LIFETIME"
        ].total_seconds()
    )

        self.assertAlmostEqual(
           token_lifetime,
           expected_lifetime,
           delta=1,
    )

    def test_bearer_access_token_authentication_works(self):
        """
        Valid Bearer access token must authenticate the user.
        """
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {str(self.access)}"
        )

        response = self.client.get(
            self.me_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_invalid_access_token_is_rejected(self):
        """
        Invalid access token must be rejected.
        """
        self.client.credentials(
            HTTP_AUTHORIZATION="Bearer invalid-token"
        )

        response = self.client.get(
            self.me_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_refresh_token_cannot_authenticate_protected_endpoint(self):
        """
        Refresh token must not be usable as an access token.
        """
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {str(self.refresh)}"
        )

        response = self.client.get(
            self.me_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_refresh_rotation_is_enabled(self):
        """
        Refresh token rotation must be enabled.
        """
        self.assertTrue(
            settings.SIMPLE_JWT[
                "ROTATE_REFRESH_TOKENS"
            ]
        )

    def test_blacklist_after_rotation_is_enabled(self):
        """
        Old refresh tokens must be blacklisted after rotation.
        """
        self.assertTrue(
            settings.SIMPLE_JWT[
                "BLACKLIST_AFTER_ROTATION"
            ]
        )

def test_refresh_token_lifetime_configuration(self):
    token_lifetime = self.refresh["exp"] - self.refresh["iat"]

    expected_lifetime = int(
        settings.SIMPLE_JWT[
            "REFRESH_TOKEN_LIFETIME"
        ].total_seconds()
    )

    self.assertAlmostEqual(
        token_lifetime,
        expected_lifetime,
        delta=1,
    )      