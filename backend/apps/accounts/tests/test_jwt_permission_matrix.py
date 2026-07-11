from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class JWTPermissionMatrixTestCase(APITestCase):
    """
    Sprint 3.2.7.7
    JWT Permission Matrix & Endpoint Protection
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username="permission_user",
            email="permission@example.com",
            password="StrongPassword123!",
        )

        refresh = RefreshToken.for_user(self.user)

        self.access_token = str(refresh.access_token)
        self.refresh_token = str(refresh)

        self.me_url = reverse("accounts:me")

    # ---------------------------------------------------
    # Helper
    # ---------------------------------------------------

    def auth(self, token):
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )

    # ---------------------------------------------------
    # Tests
    # ---------------------------------------------------

    def test_authenticated_user_can_access_me(self):
        self.auth(self.access_token)

        response = self.client.get(self.me_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_request_without_token_returns_401(self):
        response = self.client.get(self.me_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_invalid_access_token_returns_401(self):
        self.auth("invalid.token.value")

        response = self.client.get(self.me_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_refresh_token_cannot_access_protected_endpoint(self):
        self.auth(self.refresh_token)

        response = self.client.get(self.me_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_malformed_authorization_header_returns_401(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=self.access_token
        )

        response = self.client.get(self.me_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_wrong_authentication_scheme_returns_401(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {self.access_token}"
        )

        response = self.client.get(self.me_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_inactive_user_cannot_access_endpoint(self):
        self.user.is_active = False
        self.user.save(update_fields=["is_active"])

        self.auth(self.access_token)

        response = self.client.get(self.me_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )