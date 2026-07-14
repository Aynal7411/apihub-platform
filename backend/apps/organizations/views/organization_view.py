from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.organizations.models import Organization
from apps.organizations.permissions.organization_permissions import (
    OrganizationRolePermission,
)
from apps.organizations.serializers.organization_serializer import (
    OrganizationCreateSerializer,
    OrganizationSerializer,
    OrganizationUpdateSerializer,
)
from apps.organizations.services.organization_service import (
    OrganizationService,
)



class OrganizationListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        return Organization.objects.filter(
            memberships__user=user,
            memberships__is_active=True,
            is_active=True,
        ).distinct()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return OrganizationCreateSerializer

        return OrganizationSerializer

    def create(self, request, *args, **kwargs):
        input_serializer = self.get_serializer(
            data=request.data
        )
        input_serializer.is_valid(raise_exception=True)

        organization = input_serializer.save()

        output_serializer = OrganizationSerializer(
            organization,
            context=self.get_serializer_context(),
        )

        return Response(
            output_serializer.data,
            status=status.HTTP_201_CREATED,
        )
    



class OrganizationDetailAPIView(
    generics.RetrieveUpdateDestroyAPIView
):
    permission_classes = [
        IsAuthenticated,
        OrganizationRolePermission,
    ]

    lookup_field = "id"

    def get_queryset(self):
        return Organization.objects.filter(
            is_active=True,
            memberships__user=self.request.user,
            memberships__is_active=True,
        ).distinct()

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return OrganizationUpdateSerializer

        return OrganizationSerializer

    def perform_update(self, serializer):
        organization = self.get_object()

        OrganizationService.update_organization(
            organization=organization,
            **serializer.validated_data,
        )

    def destroy(self, request, *args, **kwargs):
        organization = self.get_object()

        OrganizationService.deactivate_organization(
            organization=organization,
        )

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )   