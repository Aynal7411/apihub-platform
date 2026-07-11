from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from .serializers.auth import LoginSerializer
from .services.auth_service import AuthService
from .serializers.auth import RegistrationSerializer
from .services.auth_service import AuthService
from apps.common.utils import success_response
from rest_framework.permissions import AllowAny

class RegistrationAPIView(GenericAPIView):

    serializer_class = RegistrationSerializer
    permission_classes = []

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