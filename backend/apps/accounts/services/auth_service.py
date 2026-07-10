from django.contrib.auth import get_user_model

User = get_user_model()


class AuthService:

    @staticmethod
    def register_user(validated_data):

        validated_data.pop("password_confirm")

        password = validated_data.pop("password")

        user = User.objects.create_user(
            password=password,
            **validated_data,
        )

        return user