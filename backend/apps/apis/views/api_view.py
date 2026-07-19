from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from apps.apis.models import API
from apps.apis.serializers import APISerializer
from apps.apis.selectors import APISelector
from apps.apis.services import APIService
from apps.organizations.models import Organization


class APIListCreateView(generics.ListCreateAPIView):
    """
    GET  -> List APIs
    POST -> Create API
    """

    serializer_class = APISerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Return APIs for the user's organization.
        """

        organization = Organization.objects.first()

        return APISelector.list_organization_apis(
            organization
        )

    def perform_create(self, serializer):
        """
        Create API using service layer.
        """

        organization = Organization.objects.first()

        APIService.create_api(
            organization=organization,
            created_by=self.request.user,
            name=serializer.validated_data["name"],
            summary=serializer.validated_data["summary"],
            description=serializer.validated_data.get(
                "description",
                "",
            ),
            category=serializer.validated_data.get(
                "category",
                API.Category.UTILITY,
            ),
            visibility=serializer.validated_data.get(
                "visibility",
                API.Visibility.PRIVATE,
            ),
            auth_type=serializer.validated_data.get(
                "auth_type",
                API.AuthType.API_KEY,
            ),
            website=serializer.validated_data.get(
                "website",
                "",
            ),
            docs_url=serializer.validated_data.get(
                "docs_url",
                "",
            ),
        )


class APIRetrieveView(generics.RetrieveAPIView):

    serializer_class = APISerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def get_object(self):
        return APISelector.get_api_by_id(
            self.kwargs["id"]
        )        
    
class APIUpdateView(generics.UpdateAPIView):

    serializer_class = APISerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def get_object(self):
        return APISelector.get_api_by_id(
            self.kwargs["id"]
        )

    def perform_update(self, serializer):

        api = self.get_object()

        APIService.update_api(
            api=api,
            **serializer.validated_data,
        )    


class APIDeleteView(generics.DestroyAPIView):

    serializer_class = APISerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def get_object(self):
        return APISelector.get_api_by_id(
            self.kwargs["id"]
        )

    def perform_destroy(self, instance):

        APIService.soft_delete_api(
            api=instance,
            deleted_by=self.request.user,
        )

    def destroy(self, request, *args, **kwargs):

        instance = self.get_object()

        self.perform_destroy(instance)

        return Response(
            {
                "message": "API deleted successfully."
            },
            status=status.HTTP_200_OK,
        )        