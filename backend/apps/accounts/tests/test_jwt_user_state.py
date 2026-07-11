from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.services.token_service import TokenService


User = get_user_model()


class JWTUserStateTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="jwtstateuser",
            email="jwtstate@example.com",
            password="StrongPassword123!",
        )

        self.me_url = reverse("accounts:me")

        self.tokens = TokenService.create_tokens_for_user(
            self.user
        )

        self.access_token = self.tokens["access"]

    def authenticate(self, token=None):
        token = token or self.access_token

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )

    def test_active_user_can_access_current_user_endpoint(self):
        self.authenticate()

        response = self.client.get(self.me_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_inactive_user_cannot_access_current_user_endpoint(self):
        self.user.is_active = False
        self.user.save(update_fields=["is_active"])

        self.authenticate()

        response = self.client.get(self.me_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_token_issued_before_deactivation_is_rejected(self):
        old_access_token = self.access_token

        self.user.is_active = False
        self.user.save(update_fields=["is_active"])

        self.authenticate(old_access_token)

        response = self.client.get(self.me_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_deleted_user_token_is_rejected(self):
        access_token = self.access_token

        self.user.delete()

        self.authenticate(access_token)

        response = self.client.get(self.me_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_invalid_access_token_returns_401(self):
        self.authenticate(
            "invalid.jwt.token"
        )

        response = self.client.get(self.me_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_authentication_error_has_standard_response_structure(self):
        self.authenticate(
            "invalid.jwt.token"
        )

        response = self.client.get(self.me_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

        self.assertIn("success", response.data)
        self.assertIn("message", response.data)

        self.assertFalse(
            response.data["success"]
        )