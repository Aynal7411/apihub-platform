from rest_framework_simplejwt.tokens import RefreshToken


class TokenService:

    @staticmethod
    def create_tokens_for_user(user):
        refresh = RefreshToken.for_user(user)

        # Minimal user-context claims
        refresh["email"] = user.email
        refresh["is_active"] = user.is_active

        # Add only if your User model has `role`
        if hasattr(user, "role"):
            refresh["role"] = user.role

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }