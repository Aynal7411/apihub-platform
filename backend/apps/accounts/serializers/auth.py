from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

User = get_user_model()


class RegistrationSerializer(serializers.Serializer):

    email = serializers.EmailField()

    username = serializers.CharField(max_length=150)

    password = serializers.CharField(
        write_only=True,
        min_length=8,
    )

    password_confirm = serializers.CharField(
        write_only=True,
    )

    first_name = serializers.CharField(
        required=False,
        allow_blank=True,
    )

    last_name = serializers.CharField(
        required=False,
        allow_blank=True,
    )

    def validate_email(self, value):
        email = value.strip().lower()
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                "Email already exists."
            )

        return email
    def validate_username(self, value):

        username = value.strip()
        if User.objects.filter(username__iexact=username).exists():
            raise serializers.ValidationError(
                "Username already exists."
            )

        return username

    def validate(self, attrs):

        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {
                    "password_confirm":
                        "Passwords do not match."
                }
            )

        validate_password(attrs["password"])

        return attrs