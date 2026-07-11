from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from apps.accounts.services.token_service import TokenService


User = get_user_model()


class JWTCustomClaimsTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="claimsuser",
            email="claims@example.com",
            password="StrongPassword123!",
        )

        self.tokens = TokenService.create_tokens_for_user(
            self.user
        )

        self.access_token = self.tokens["access"]
        self.refresh_token = self.tokens["refresh"]

    def test_access_token_contains_user_id(self):
        token = AccessToken(self.access_token)

        self.assertIn("user_id", token)
        self.assertEqual(
            str(token["user_id"]),
            str(self.user.id),
        )

    def test_access_token_contains_email(self):
        token = AccessToken(self.access_token)

        self.assertIn("email", token)
        self.assertEqual(
            token["email"],
            self.user.email,
        )

    def test_access_token_contains_is_active(self):
        token = AccessToken(self.access_token)

        self.assertIn("is_active", token)
        self.assertEqual(
            token["is_active"],
            self.user.is_active,
        )

    def test_refresh_token_contains_custom_claims(self):
        token = RefreshToken(self.refresh_token)

        self.assertEqual(
            token["email"],
            self.user.email,
        )

        self.assertEqual(
            token["is_active"],
            self.user.is_active,
        )

    def test_role_claim_if_user_model_supports_role(self):
        token = AccessToken(self.access_token)

        if hasattr(self.user, "role"):
            self.assertIn("role", token)
            self.assertEqual(
                token["role"],
                self.user.role,
            )

    def test_sensitive_password_data_is_not_exposed(self):
        access_token = AccessToken(self.access_token)
        refresh_token = RefreshToken(self.refresh_token)

        forbidden_claims = [
            "password",
            "password_hash",
            "secret",
            "api_key",
        ]

        for claim in forbidden_claims:
            self.assertNotIn(claim, access_token)
            self.assertNotIn(claim, refresh_token)

    def test_access_token_can_authenticate_current_user(self):
        me_url = reverse("accounts:me")

        self.client.credentials(
            HTTP_AUTHORIZATION=(
                f"Bearer {self.access_token}"
            )
        )

        response = self.client.get(me_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )