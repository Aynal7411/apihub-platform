from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
)

from apps.accounts.models import User


class RefreshTokenRotationAPITestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="rotation@example.com",
            username="rotationuser",
            password="StrongPassword123!",
        )

        self.login_url = reverse("accounts:login")
        self.refresh_url = reverse("accounts:token-refresh")

        # Login and get the initial refresh token
        response = self.client.post(
            self.login_url,
            {
                "email": "rotation@example.com",
                "password": "StrongPassword123!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.old_refresh = response.data["data"]["refresh"]

    def test_refresh_returns_new_access_and_refresh_token(self):
        response = self.client.post(
            self.refresh_url,
            {
                "refresh": self.old_refresh,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertTrue(response.data["success"])

        self.assertIn(
            "access",
            response.data["data"],
        )

        self.assertIn(
            "refresh",
            response.data["data"],
        )

        new_refresh = response.data["data"]["refresh"]

        self.assertNotEqual(
            self.old_refresh,
            new_refresh,
        )

    def test_old_refresh_token_is_blacklisted_after_rotation(self):
        response = self.client.post(
            self.refresh_url,
            {
                "refresh": self.old_refresh,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertTrue(
            BlacklistedToken.objects.exists()
        )

        # Try using the old refresh token again
        second_response = self.client.post(
            self.refresh_url,
            {
                "refresh": self.old_refresh,
            },
            format="json",
        )

        self.assertEqual(
            second_response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_rotated_refresh_token_can_be_used(self):
        first_response = self.client.post(
            self.refresh_url,
            {
                "refresh": self.old_refresh,
            },
            format="json",
        )

        self.assertEqual(
            first_response.status_code,
            status.HTTP_200_OK,
        )

        new_refresh = first_response.data["data"]["refresh"]

        second_response = self.client.post(
            self.refresh_url,
            {
                "refresh": new_refresh,
            },
            format="json",
        )

        self.assertEqual(
            second_response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn(
            "access",
            second_response.data["data"],
        )

        self.assertIn(
            "refresh",
            second_response.data["data"],
        )

    def test_invalid_refresh_token_is_rejected(self):
        response = self.client.post(
            self.refresh_url,
            {
                "refresh": "invalid-refresh-token",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_missing_refresh_token_is_rejected(self):
        response = self.client.post(
            self.refresh_url,
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )