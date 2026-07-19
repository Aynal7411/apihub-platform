from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.apis.models import APIEndpoint


class APIEndpointService:
    """
    Business logic for API Endpoints.
    """

    @staticmethod
    @transaction.atomic
    def create_endpoint(version, **data):
        """
        Create a new endpoint.
        """

        if APIEndpoint.objects.filter(
            version=version,
            path=data["path"],
            method=data["method"],
            is_active=True,
        ).exists():
            raise ValidationError(
                "Endpoint already exists for this version."
            )

        endpoint = APIEndpoint.objects.create(
            version=version,
            **data,
        )

        return endpoint

    @staticmethod
    @transaction.atomic
    def update_endpoint(endpoint, **data):
        """
        Update endpoint.
        """

        for field, value in data.items():
            setattr(endpoint, field, value)

        endpoint.save()

        return endpoint

    @staticmethod
    @transaction.atomic
    def activate_endpoint(endpoint):
        """
        Activate endpoint.
        """

        endpoint.is_active = True
        endpoint.save(update_fields=["is_active"])

        return endpoint

    @staticmethod
    @transaction.atomic
    def deactivate_endpoint(endpoint):
        """
        Deactivate endpoint.
        """

        endpoint.is_active = False
        endpoint.save(update_fields=["is_active"])

        return endpoint

    @staticmethod
    @transaction.atomic
    def delete_endpoint(endpoint):
        """
        Soft delete endpoint.
        """

        endpoint.is_active = False

        if hasattr(endpoint, "deleted_at"):
            endpoint.deleted_at = timezone.now()

        endpoint.save()

        return endpoint