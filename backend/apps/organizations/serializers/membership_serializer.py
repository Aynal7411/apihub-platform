from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.organizations.models import OrganizationMembership

User = get_user_model()


class OrganizationMembershipSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        source="user.email",
        read_only=True,
    )

    class Meta:
        model = OrganizationMembership
        fields = [
            "id",
            "email",
            "role",
            "is_active",
            "joined_at",
        ]


class AddOrganizationMemberSerializer(serializers.Serializer):
    email = serializers.EmailField()

    role = serializers.ChoiceField(
        choices=[
            OrganizationMembership.Role.ADMIN,
            OrganizationMembership.Role.DEVELOPER,
            OrganizationMembership.Role.VIEWER,
        ],
        default=OrganizationMembership.Role.VIEWER,
    )

    def validate_email(self, value):
        try:
            return User.objects.get(email__iexact=value)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                "No registered user found with this email."
            )


class UpdateOrganizationMemberSerializer(serializers.Serializer):
    role = serializers.ChoiceField(
        choices=[
            OrganizationMembership.Role.ADMIN,
            OrganizationMembership.Role.DEVELOPER,
            OrganizationMembership.Role.VIEWER,
        ]
    )