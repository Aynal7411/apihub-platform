from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from rest_framework_simplejwt.tokens import RefreshToken


User = get_user_model()


class RefreshTokenAPITestCase(APITestCase):

    def setUp(self):
        self.url = reverse("accounts:token-refresh")

        self.user = User.objects.create_user(
            email="refresh@example.com",
            username="refreshuser",
            password="StrongPassword123!",
        )

        refresh = RefreshToken.for_user(self.user)
        self.refresh_token = str(refresh)

    def test_refresh_token_success(self):
        response = self.client.post(
            self.url,
            {
                "refresh": self.refresh_token,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertTrue(response.data["success"])

        self.assertEqual(
            response.data["message"],
            "Access token refreshed successfully.",
        )

        self.assertIn("data", response.data)
        self.assertIn("access", response.data["data"])

    def test_refresh_token_missing(self):
        response = self.client.post(
            self.url,
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_refresh_token_invalid(self):
        response = self.client.post(
            self.url,
            {
                "refresh": "invalid-refresh-token",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )