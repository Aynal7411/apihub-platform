from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase


User = get_user_model()


class JWTLoginSecurityTestCase(APITestCase):

    def setUp(self):
        self.login_url = reverse("accounts:login")

        self.password = "StrongPassword123!"

        self.user = User.objects.create_user(
            username="jwtloginuser",
            email="jwtlogin@example.com",
            password=self.password,
        )

        self.valid_credentials = {
            "email": self.user.email,
            "password": self.password,
        }

    def test_active_user_can_login_and_receive_tokens(self):
        response = self.client.post(
            self.login_url,
            self.valid_credentials,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertTrue(response.data["success"])
        self.assertIn("data", response.data)

        data = response.data["data"]

        # Adjust these two lines only if your login response
        # stores tokens inside data["tokens"].
        self.assertIn("access", data)
        self.assertIn("refresh", data)

    def test_wrong_password_returns_401(self):
        response = self.client.post(
            self.login_url,
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

    def test_nonexistent_user_returns_401(self):
        response = self.client.post(
            self.login_url,
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

    def test_inactive_user_cannot_receive_tokens(self):
        self.user.is_active = False
        self.user.save(update_fields=["is_active"])

        response = self.client.post(
            self.login_url,
            self.valid_credentials,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

        data = response.data.get("data") or {}

        self.assertNotIn("access", data)
        self.assertNotIn("refresh", data)

    def test_password_is_never_exposed_in_success_response(self):
        response = self.client.post(
            self.login_url,
            self.valid_credentials,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        response_text = str(response.data)

        self.assertNotIn(
            self.password,
            response_text,
        )

        self.assertNotIn(
            "password",
            response.data.get("data", {}),
        )

    def test_failed_login_does_not_issue_tokens(self):
        response = self.client.post(
            self.login_url,
            {
                "email": self.user.email,
                "password": "InvalidPassword!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

        data = response.data.get("data") or {}

        self.assertNotIn("access", data)
        self.assertNotIn("refresh", data)

    def test_login_error_has_standard_response_structure(self):
        response = self.client.post(
            self.login_url,
            {
                "email": self.user.email,
                "password": "InvalidPassword!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

        self.assertIn("success", response.data)
        self.assertIn("message", response.data)

        self.assertFalse(response.data["success"])