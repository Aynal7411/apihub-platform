from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User


class RegistrationAPITest(APITestCase):

    def setUp(self):
        self.url = reverse("register")

        self.payload = {
            "email": "john@example.com",
            "username": "john",
            "password": "StrongPass123!",
            "password_confirm": "StrongPass123!",
            "first_name": "John",
            "last_name": "Doe",
        }

    def test_user_registration_success(self):

        response = self.client.post(
            self.url,
            self.payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertTrue(
            User.objects.filter(
                email="john@example.com"
            ).exists()
        )

    def test_duplicate_email(self):

        User.objects.create_user(
            email="john@example.com",
            username="john1",
            password="StrongPass123!",
        )

        response = self.client.post(
            self.url,
            self.payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_duplicate_username(self):

        User.objects.create_user(
            email="another@example.com",
            username="john",
            password="StrongPass123!",
        )

        response = self.client.post(
            self.url,
            self.payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_password_mismatch(self):

        payload = self.payload.copy()
        payload["password_confirm"] = "WrongPassword"

        response = self.client.post(
            self.url,
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_weak_password(self):

        payload = self.payload.copy()
        payload["password"] = "123"
        payload["password_confirm"] = "123"

        response = self.client.post(
            self.url,
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )