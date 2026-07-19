from django.db.models import QuerySet
from django.shortcuts import get_object_or_404

from apps.apis.models import APIVersion


class APIVersionSelector:
    """
    Read-only queries for API versions.
    """

    @staticmethod
    def get_version_by_id(version_id) -> APIVersion:
        return get_object_or_404(
            APIVersion.objects.select_related("api"),
            id=version_id,
        )

    @staticmethod
    def get_version(api, version: str) -> APIVersion:
        return get_object_or_404(
            APIVersion.objects.select_related("api"),
            api=api,
            version=version,
        )

    @staticmethod
    def get_default_version(api) -> APIVersion:
        return get_object_or_404(
            APIVersion.objects.select_related("api"),
            api=api,
            is_default=True,
        )

    @staticmethod
    def list_versions(api) -> QuerySet:
        return (
            APIVersion.objects.filter(api=api)
            .select_related("api")
            .order_by("-created_at")
        )

    @staticmethod
    def list_active_versions(api) -> QuerySet:
        return (
            APIVersion.objects.filter(
                api=api,
                status=APIVersion.Status.ACTIVE,
            )
            .select_related("api")
            .order_by("-created_at")
        )