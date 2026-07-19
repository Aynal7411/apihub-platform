from django.shortcuts import get_object_or_404

from apps.apis.models import APIEndpoint


class APIEndpointSelector:
    """
    Read-only queries for APIEndpoint.
    """

    @staticmethod
    def list_endpoints(version):
        """
        Return all active endpoints for a version.
        """
        return (
            APIEndpoint.objects
            .filter(
                version=version,
                is_active=True,
            )
            .order_by("path", "method")
        )

    @staticmethod
    def get_endpoint(endpoint_id):
        """
        Return one active endpoint by UUID.
        """
        return get_object_or_404(
            APIEndpoint,
            id=endpoint_id,
            is_active=True,
        )

    @staticmethod
    def get_endpoint_by_path(version, path, method):
        """
        Find endpoint using version + path + method.
        """
        return (
            APIEndpoint.objects
            .filter(
                version=version,
                path=path,
                method=method,
                is_active=True,
            )
            .first()
        )

    @staticmethod
    def get_active_endpoints(version):
        """
        Return active endpoints only.
        """
        return (
            APIEndpoint.objects
            .filter(
                version=version,
                is_active=True,
            )
            .order_by("path", "method")
        )

    @staticmethod
    def endpoint_exists(version, path, method):
        """
        Check whether an endpoint already exists.
        """
        return APIEndpoint.objects.filter(
            version=version,
            path=path,
            method=method,
            is_active=True,
        ).exists()

    @staticmethod
    def count_endpoints(version):
        """
        Return total active endpoints for a version.
        """
        return APIEndpoint.objects.filter(
            version=version,
            is_active=True,
        ).count()