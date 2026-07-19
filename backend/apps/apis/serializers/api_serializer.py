from rest_framework import serializers

from apps.apis.models import API


class APISerializer(serializers.ModelSerializer):

    organization_name = serializers.CharField(
        source="organization.name",
        read_only=True,
    )

    created_by_email = serializers.EmailField(
        source="created_by.email",
        read_only=True,
    )

    class Meta:
        model = API

        fields = (
            "id",
            "organization",
            "organization_name",
            "created_by",
            "created_by_email",
            "name",
            "slug",
            "summary",
            "description",
            "category",
            "visibility",
            "lifecycle",
            "auth_type",
            "website",
            "docs_url",
            "is_active",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "slug",
            "created_by",
            "created_at",
            "updated_at",
        )

    def validate_name(self, value):

        value = value.strip()

        if len(value) < 3:
            raise serializers.ValidationError(
                "API name must contain at least 3 characters."
            )

        return value

    def validate_summary(self, value):

        value = value.strip()

        if len(value) < 10:
            raise serializers.ValidationError(
                "Summary must contain at least 10 characters."
            )

        return value
    
    def validate(self, attrs):
        """
        Cross-field validation.
        """

        website = attrs.get("website")
        docs_url = attrs.get("docs_url")

        if website and docs_url:
            if website == docs_url:
                raise serializers.ValidationError(
                    "Website and documentation URL cannot be the same."
                )

        return attrs
