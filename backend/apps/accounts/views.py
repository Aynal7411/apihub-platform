from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from .serializers.auth import LoginSerializer
from .services.auth_service import AuthService
from .serializers.auth import RegistrationSerializer
from .services.auth_service import AuthService
from apps.common.utils import success_response
from.serializers.auth import UserSerializer
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from .serializers.auth import RefreshTokenSerializer
from apps.accounts.serializers.auth import LogoutSerializer
from apps.accounts.serializers.auth import VerifyEmailSerializer
from apps.accounts.serializers.auth import (
    ResendVerificationSerializer,
)
from django.db import transaction

from apps.accounts.tasks import (
    send_verification_email_task,
    send_password_reset_email_task,
)
from apps.accounts.services.verification_email_service import (
    VerificationEmailService,
)
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.token_blacklist.models import (
    OutstandingToken,
    BlacklistedToken,
)
from apps.accounts.services.email_verification_service import (
    EmailVerificationService,
)

User = get_user_model()

class RegistrationAPIView(GenericAPIView):

    serializer_class = RegistrationSerializer
    permission_classes = [AllowAny]

    authentication_classes = []

     
    def post(self, request):

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        user = AuthService.register_user(
            serializer.validated_data
        )
        
        return success_response(
         message="Registration successful.",
         data={
          "id": str(user.id),
          "email": user.email,
          "username": user.username,
           },
        status_code=status.HTTP_201_CREATED,
        )
    

class LoginAPIView(GenericAPIView):
    """
    Authenticate a user using email and password
    and return JWT access and refresh tokens.
    """

    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = AuthService.login(
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
        )

        user = result["user"]

        return success_response(
            message="Login successful.",
            data={
                "access": result["access"],
                "refresh": result["refresh"],
                "user": {
                    "id": str(user.id),
                    "email": user.email,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                },
            },
            status_code=status.HTTP_200_OK,
        )
    

class RefreshTokenAPIView(GenericAPIView):
    serializer_class = RefreshTokenSerializer
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return success_response(
            message="Access token refreshed successfully.",
            data=serializer.validated_data,
            status_code=status.HTTP_200_OK,
        )

from rest_framework.generics import RetrieveAPIView

class CurrentUserAPIView(GenericAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user)

        return success_response(
            message="Current user retrieved successfully.",
            data=serializer.data,
        )    


class LogoutAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        print(request.user)
        print(request.auth)
        serializer = LogoutSerializer(data=request.data)
        print(request.data)
        serializer.is_valid(raise_exception=True)

        refresh = serializer.validated_data["refresh"]


        AuthService.logout(
            serializer.validated_data["refresh"]
        )

        return success_response(
            message="Logout successful.",
            data=None,
            status_code=status.HTTP_200_OK,
        )      
    

class LogoutAllAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        revoked_sessions = AuthService.logout_all(
            user=request.user
        )

        return success_response(
            message="Logged out from all devices successfully.",
            data={
                "revoked_sessions": revoked_sessions,
            },
            status_code=status.HTTP_200_OK,
        )
    

class SessionListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tokens = (
            OutstandingToken.objects
            .filter(user=request.user)
            .exclude(blacklistedtoken__isnull=False)
            .order_by("-created_at")
        )

        sessions = [
            {
                "id": token.id,
                "jti": token.jti,
                "created_at": token.created_at,
                "expires_at": token.expires_at,
            }
            for token in tokens
        ]

        return success_response(
            message="Active sessions retrieved successfully.",
             data={
                "sessions": sessions,
            },
            status_code=status.HTTP_200_OK,
        )


class SessionRevokeAPIView(APIView):
    permission_classes = [IsAuthenticated]


    def delete(self, request, session_id):
        try:
            token = OutstandingToken.objects.get(
                id=session_id,
                user=request.user,
            )
        except OutstandingToken.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "message": "Session not found.",
                    "errors": None,
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        BlacklistedToken.objects.get_or_create(
            token=token
        )

        return success_response(
            message="Session revoked successfully.",
            data={
                "session_id": token.id,
            },
            status_code=status.HTTP_200_OK,
        )
    def post(self, request, session_id):
        try:
            token = OutstandingToken.objects.get(
                id=session_id,
                user=request.user,
            )
        except OutstandingToken.DoesNotExist:
            return success_response(
                message="Session not found.",
                data=None,
                status_code=status.HTTP_404_NOT_FOUND,
            )

        BlacklistedToken.objects.get_or_create(
            token=token
        )

        return success_response(
            message="Session revoked successfully.",
            data=None,
            status_code=status.HTTP_200_OK,
        )


class VerifyEmailAPIView(GenericAPIView):
    """
    Verify a user's email address using a secure,
    single-use verification token.
    """

    serializer_class = VerifyEmailSerializer
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        user = EmailVerificationService.verify_token(
            raw_token=serializer.validated_data["token"]
        )

        return success_response(
            message="Email verified successfully.",
            data={
                "user_id": str(user.id),
                "email": user.email,
                "is_email_verified": user.is_email_verified,
                "email_verified_at": user.email_verified_at,
            },
            status_code=status.HTTP_200_OK,
        )

class ResendVerificationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        if user.is_email_verified:
            return Response(
                {
                    "success": False,
                    "message": "Email address is already verified.",
                    "data": None,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Prevent rapid resend requests
        EmailVerificationService.enforce_resend_cooldown(user)

        # Queue email only after the database transaction commits
        transaction.on_commit(
            lambda: send_verification_email_task.delay(
                user.pk,
                invalidate_existing=True,
            )
        )

        return Response(
            {
                "success": True,
                "message": "Verification email has been queued.",
                "data": None,
            },
            status=status.HTTP_200_OK,
        )
    
from apps.accounts.serializers.auth import  PasswordResetRequestSerializer
  


from apps.accounts.services.password_reset_service import (
    PasswordResetService
)

class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]

        user = (
            User.objects
            .filter(email=email)
            .first()
        )

        # Enumeration protection
        if user:
            token = PasswordResetService.create_token(user)

            transaction.on_commit(
                lambda: send_password_reset_email_task.delay(
                    user.pk,
                    token.pk,
                )
            )

        return Response(
            {
                "success": True,
                "message": (
                    "If an account exists, "
                    "a password reset email has been sent."
                ),
            }
        )