from rest_framework import serializers

from apps.apis.models import APIVersion


class APIVersionSerializer(serializers.ModelSerializer):

    api_name = serializers.CharField(
        source="api.name",
        read_only=True,
    )

    class Meta:
        model = APIVersion

        fields = (
            "id",
            "api",
            "api_name",
            "version",
            "title",
            "description",
            "base_path",
            "status",
            "is_default",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )

    def validate_version(self, value):
        """
        Validate version format.
        """

        value = value.strip().lower()

        if not value.startswith("v"):
            raise serializers.ValidationError(
                "Version must start with 'v' (e.g. v1, v2, v1.1)."
            )

        return value

    def validate_base_path(self, value):
        """
        Validate base path.
        """

        if not value.startswith("/"):
            raise serializers.ValidationError(
                "Base path must start with '/'."
            )

        return value