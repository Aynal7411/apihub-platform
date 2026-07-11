from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase


User = get_user_model()


class LoginAPITestCase(APITestCase):

    def setUp(self):
        self.url = reverse("accounts:login")

        self.password = "StrongPass123!"

        self.user = User.objects.create_user(
            email="test@example.com",
            username="testuser",
            password=self.password,
        )

    def test_login_success(self):
        response = self.client.post(
            self.url,
            {
                "email": self.user.email,
                "password": self.password,
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
            "Login successful.",
        )

    def test_login_returns_jwt_tokens(self):
        response = self.client.post(
            self.url,
            {
                "email": self.user.email,
                "password": self.password,
            },
            format="json",
        )

        data = response.data["data"]

        self.assertIn("access", data)
        self.assertIn("refresh", data)

        self.assertTrue(data["access"])
        self.assertTrue(data["refresh"])

    def test_login_with_invalid_password(self):
        response = self.client.post(
            self.url,
            {
                "email": self.user.email,
                "password": "WrongPassword123!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_login_with_nonexistent_email(self):
        response = self.client.post(
            self.url,
            {
                "email": "unknown@example.com",
                "password": self.password,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_login_with_missing_credentials(self):
        response = self.client.post(
            self.url,
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_inactive_user_cannot_login(self):
        self.user.is_active = False
        self.user.save(update_fields=["is_active"])

        response = self.client.post(
            self.url,
            {
                "email": self.user.email,
                "password": self.password,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )