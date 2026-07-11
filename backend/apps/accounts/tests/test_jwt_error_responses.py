from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken


class JWTErrorResponsesTestCase(APITestCase):

    def setUp(self):
        self.me_url = reverse("accounts:me")
        self.refresh_url = reverse("accounts:token-refresh")

    def test_missing_access_token_returns_401(self):
        response = self.client.get(self.me_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_invalid_access_token_returns_401(self):
        self.client.credentials(
            HTTP_AUTHORIZATION="Bearer invalid-access-token"
        )

        response = self.client.get(self.me_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_invalid_refresh_token_returns_401(self):
        response = self.client.post(
            self.refresh_url,
            {"refresh": "invalid-refresh-token"},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_missing_refresh_token_returns_400(self):
        response = self.client.post(
            self.refresh_url,
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_error_response_has_standard_structure(self):
        self.client.credentials(
            HTTP_AUTHORIZATION="Bearer invalid-access-token"
        )

        response = self.client.get(self.me_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

        self.assertIn("success", response.data)
        self.assertIn("message", response.data)
        self.assertIn("errors", response.data)

        self.assertFalse(response.data["success"])