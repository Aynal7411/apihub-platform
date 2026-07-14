from django.shortcuts import get_object_or_404

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.organizations.models import (
    Organization,
    OrganizationMembership,
)
from apps.organizations.permissions.organization_permissions import (
    CanManageOrganizationMembers,
)
from apps.organizations.serializers.membership_serializer import (
    AddOrganizationMemberSerializer,
    OrganizationMembershipSerializer,
    UpdateOrganizationMemberSerializer,
)
from apps.organizations.services.membership_service import (
    OrganizationMembershipService,
)


class OrganizationMemberListCreateAPIView(
    generics.ListCreateAPIView
):
    permission_classes = [
        IsAuthenticated,
        CanManageOrganizationMembers,
    ]

    def get_organization(self):
        if not hasattr(self, "_organization"):
            self._organization = get_object_or_404(
                Organization,
                id=self.kwargs["organization_id"],
                is_active=True,
            )

        return self._organization

    def get_queryset(self):
        return OrganizationMembership.objects.filter(
            organization=self.get_organization(),
            is_active=True,
        ).select_related("user")

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AddOrganizationMemberSerializer

        return OrganizationMembershipSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        membership = OrganizationMembershipService.add_member(
            organization=self.get_organization(),
            user=serializer.validated_data["email"],
            role=serializer.validated_data["role"],
        )

        output_serializer = OrganizationMembershipSerializer(
            membership
        )

        return Response(
            output_serializer.data,
            status=status.HTTP_201_CREATED,
        )
    
class OrganizationMemberDetailAPIView(
    generics.RetrieveUpdateDestroyAPIView
):
    permission_classes = [
        IsAuthenticated,
        CanManageOrganizationMembers,
    ]

    lookup_url_kwarg = "membership_id"

    def get_organization(self):
        if not hasattr(self, "_organization"):
            self._organization = get_object_or_404(
                Organization,
                id=self.kwargs["organization_id"],
                is_active=True,
            )

        return self._organization

    def get_queryset(self):
        return OrganizationMembership.objects.filter(
            organization=self.get_organization(),
            is_active=True,
        ).select_related("user")

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return UpdateOrganizationMemberSerializer

        return OrganizationMembershipSerializer

    def update(self, request, *args, **kwargs):
        membership = self.get_object()

        serializer = self.get_serializer(
            data=request.data,
            partial=kwargs.pop("partial", False),
        )
        serializer.is_valid(raise_exception=True)

        membership = OrganizationMembershipService.update_role(
            membership=membership,
            role=serializer.validated_data["role"],
        )

        return Response(
            OrganizationMembershipSerializer(membership).data
        )

    def destroy(self, request, *args, **kwargs):
        membership = self.get_object()

        OrganizationMembershipService.remove_member(
            membership=membership,
        )

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )   