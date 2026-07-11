from django.contrib.auth import get_user_model,aauthenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from django.core.validators import RegexValidator
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed

User = get_user_model()


class RegistrationSerializer(serializers.Serializer):

    email = serializers.EmailField(
        help_text="User email address."
    )

    username = serializers.CharField(max_length=150,
             help_text="Unique username." ,
             validators=[
            RegexValidator(
            regex=r"^[A-Za-z0-9_]+$",
            message="Only letters, numbers and underscore are allowed."
        )
    ]
             
             )                       

    password = serializers.CharField(
        write_only=True,
        min_length=8,
        trim_whitespace=False,
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
        username = value.strip().lower()
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
        attrs.pop("password_confirm")
        return attrs



class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
    )

    def validate(self, attrs):
        if not attrs.get("email"):
            raise serializers.ValidationError(
                {"email": "Email is required."}
            )

        if not attrs.get("password"):
            raise serializers.ValidationError(
                {"password": "Password is required."}
            )

        return attrs
    


from rest_framework import serializers, status
from rest_framework.exceptions import APIException

class InvalidRefreshToken(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "Invalid, expired, or blacklisted refresh token."
    default_code = "invalid_refresh_token"
   

class RefreshTokenSerializer(serializers.Serializer):
    refresh = serializers.CharField(write_only=True)

    def validate(self, attrs):
        try:
            old_refresh = RefreshToken(attrs["refresh"])

            user_id = old_refresh["user_id"]

            try:
                user = User.objects.get(pk=user_id)
            except User.DoesNotExist:
                raise InvalidRefreshToken(
                    "User associated with this token does not exist."
                )

            access_token = str(old_refresh.access_token)
            new_refresh = RefreshToken.for_user(user)

            old_refresh.blacklist()

            return {
                "access": access_token,
                "refresh": str(new_refresh),
            }

        except TokenError as exc:
            raise InvalidRefreshToken() from exc
       

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "is_active",
            
        )

        read_only_fields = fields   


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()       