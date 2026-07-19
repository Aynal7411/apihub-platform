from rest_framework import serializers

from apps.apis.models import APIEndpoint


class APIEndpointSerializer(serializers.ModelSerializer):
    class Meta:
        model = APIEndpoint

        fields = (
            "id",
            "name",
            "path",
            "method",
            "summary",
            "description",
            "authentication",
            "rate_limit",
            "is_active",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )

    def validate_path(self, value):
        """
        Endpoint path must start with '/'.
        """

        if not value.startswith("/"):
            raise serializers.ValidationError(
                "Path must start with '/'."
            )

        return value

    def validate_rate_limit(self, value):
        """
        Rate limit must be positive.
        """

        if value <= 0:
            raise serializers.ValidationError(
                "Rate limit must be greater than 0."
            )

        return value

    def validate(self, attrs):
        """
        Cross-field validation.
        """

        method = attrs.get("method")
        path = attrs.get("path")

        if method and path:
            attrs["method"] = method.upper()

        return attrs