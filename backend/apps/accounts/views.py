from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from .serializers.auth import LoginSerializer
from .services.auth_service import AuthService
from .serializers.auth import RegistrationSerializer
from .services.auth_service import AuthService
from apps.common.utils import success_response
from.serializers.auth import UserSerializer
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from .serializers.auth import RefreshTokenSerializer
from apps.accounts.serializers.auth import LogoutSerializer
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

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