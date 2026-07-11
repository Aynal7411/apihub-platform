from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from rest_framework_simplejwt.tokens import RefreshToken


User = get_user_model()


class LogoutAPITestCase(APITestCase):

    def setUp(self):
        self.url = reverse("accounts:logout")

        self.user = User.objects.create_user(
            email="logout@example.com",
            username="logoutuser",
            password="StrongPassword123!",
        )

        refresh = RefreshToken.for_user(self.user)

        self.refresh_token = str(refresh)
        self.access_token = str(refresh.access_token)

    def authenticate(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}"
        )

    def test_logout_success(self):
        self.authenticate()

        response = self.client.post(
            self.url,
            {
                "refresh": self.refresh_token
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertTrue(
            response.data["success"]
        )

    def test_logout_requires_authentication(self):
        response = self.client.post(
            self.url,
            {
                "refresh": self.refresh_token
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_logout_requires_refresh_token(self):
        self.authenticate()

        response = self.client.post(
            self.url,
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_invalid_refresh_token(self):
        self.authenticate()

        response = self.client.post(
            self.url,
            {
                "refresh": "invalid-token"
            },
            format="json",
        )

        self.assertIn(
            response.status_code,
            [
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_400_BAD_REQUEST,
            ],
        )

    def test_blacklisted_token_cannot_be_refreshed(self):
        self.authenticate()

        logout_response = self.client.post(
            self.url,
            {
                "refresh": self.refresh_token
            },
            format="json",
        )

        self.assertEqual(
            logout_response.status_code,
            status.HTTP_200_OK,
        )

        refresh_url = reverse(
            "accounts:token-refresh"
        )

        refresh_response = self.client.post(
            refresh_url,
            {
                "refresh": self.refresh_token
            },
            format="json",
        )

        self.assertIn(
            refresh_response.status_code,
            [
                status.HTTP_400_BAD_REQUEST,
                status.HTTP_401_UNAUTHORIZED,
            ],
        )