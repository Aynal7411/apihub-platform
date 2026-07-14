from rest_framework import serializers

from apps.organizations.models import Organization
from apps.organizations.services.organization_service import OrganizationService


class OrganizationSerializer(serializers.ModelSerializer):
    """
    Used for organization response/output.
    """

    owner_email = serializers.EmailField(
        source="owner.email",
        read_only=True,
    )

    class Meta:
        model = Organization
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "owner",
            "owner_email",
            "is_active",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "slug",
            "owner",
            "owner_email",
            "is_active",
            "created_at",
            "updated_at",
        ]


class OrganizationCreateSerializer(serializers.Serializer):
    """
    Validates organization creation input.
    """

    name = serializers.CharField(
        max_length=255,
    )

    description = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
    )

    def validate_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Organization name cannot be empty."
            )

        return value

    def create(self, validated_data):
        user = self.context["request"].user

        return OrganizationService.create_organization(
            user=user,
            name=validated_data["name"],
            description=validated_data.get("description", ""),
        )
    
    
class OrganizationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = [
            "name",
            "description",
        ]

    def validate_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Organization name cannot be empty."
            )

        return value  