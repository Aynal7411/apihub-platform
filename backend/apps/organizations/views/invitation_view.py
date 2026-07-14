from django.shortcuts import get_object_or_404

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.organizations.models import (
    Organization,
    OrganizationInvitation,
)
from apps.organizations.permissions.organization_permissions import (
    CanManageOrganizationMembers,
)
from apps.organizations.serializers.invitation_serializer import (
    CreateOrganizationInvitationSerializer,
    OrganizationInvitationSerializer,
)
from apps.organizations.serializers.membership_serializer import (
    OrganizationMembershipSerializer,
)
from apps.organizations.services.invitation_service import (
    OrganizationInvitationService,
)


class OrganizationInvitationListCreateAPIView(
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
        return OrganizationInvitation.objects.filter(
            organization=self.get_organization(),
        ).select_related(
            "organization",
            "invited_by",
        )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreateOrganizationInvitationSerializer

        return OrganizationInvitationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        invitation = (
            OrganizationInvitationService.create_invitation(
                organization=self.get_organization(),
                invited_by=request.user,
                **serializer.validated_data,
            )
        )

        return Response(
            OrganizationInvitationSerializer(
                invitation
            ).data,
            status=status.HTTP_201_CREATED,
        )
    

class AcceptOrganizationInvitationAPIView(
    generics.GenericAPIView
                          ):
    permission_classes = [IsAuthenticated]

    def post(self, request, token):
        invitation = get_object_or_404(
            OrganizationInvitation,
            token=token,
        )

        membership = (
            OrganizationInvitationService.accept_invitation(
                invitation=invitation,
                user=request.user,
            )
        )

        return Response(
            OrganizationMembershipSerializer(
                membership
            ).data,
            status=status.HTTP_200_OK,
        )