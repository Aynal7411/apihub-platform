from django.core import mail
from django.conf import settings
from rest_framework.test import APITestCase
from django.urls import reverse
from apps.accounts.models import User, PasswordResetToken



class PasswordResetRequestTestCase(
    APITestCase
):


    def setUp(self):

        self.user = User.objects.create_user(
             username="testuser",
            email="test@example.com",
            password="Password123"
        )


        self.url = reverse(
             "accounts:password-reset-request"
        )



    def test_password_reset_email_sent(self):

        response = self.client.post(
            self.url,
            {
                "email":
                self.user.email
            },
            format="json"
        )


        self.assertEqual(
            response.status_code,
            200
        )


        self.assertEqual(
            len(mail.outbox),
            1
        )


        self.assertTrue(
            PasswordResetToken.objects
            .filter(
                user=self.user
            )
            .exists()
        )
                                                            

   