from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView

from .serializers.auth import RegistrationSerializer
from .services.auth_service import AuthService
from apps.common.utils import success_response

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