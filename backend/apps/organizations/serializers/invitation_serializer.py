from rest_framework import serializers

from apps.organizations.models import (
    OrganizationInvitation,
    OrganizationMembership,
)


class CreateOrganizationInvitationSerializer(
    serializers.Serializer
):
    email = serializers.EmailField()

    role = serializers.ChoiceField(
        choices=[
            OrganizationMembership.Role.ADMIN,
            OrganizationMembership.Role.DEVELOPER,
            OrganizationMembership.Role.VIEWER,
        ],
        default=OrganizationMembership.Role.VIEWER,
    )


class OrganizationInvitationSerializer(
    serializers.ModelSerializer
):
    organization_name = serializers.CharField(
        source="organization.name",
        read_only=True,
    )

    invited_by_email = serializers.EmailField(
        source="invited_by.email",
        read_only=True,
    )

    class Meta:
        model = OrganizationInvitation

        fields = [
            "id",
            "organization",
            "organization_name",
            "email",
            "role",
            "status",
            "invited_by_email",
            "expires_at",
            "created_at",
            "accepted_at",
        ]