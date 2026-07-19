from django.shortcuts import get_object_or_404
from django.db.models import Q, QuerySet

from apps.apis.models import API


class APISelector:

    @staticmethod
    def get_api_by_id(api_id) -> API:
        return get_object_or_404(
            API.objects.select_related(
                "organization",
                "created_by",
            ),
            id=api_id,
            is_active=True,
        )

    @staticmethod
    def get_api_by_slug(organization, slug) -> API:
        return get_object_or_404(
            API.objects.select_related(
                "organization",
                "created_by",
            ),
            organization=organization,
            slug=slug,
            is_active=True,
        )

    @staticmethod
    def list_organization_apis(organization) -> QuerySet:
        return (
            API.objects.filter(
                organization=organization,
                is_active=True,
            )
            .select_related(
                "organization",
                "created_by",
            )
            .order_by("-created_at")
        )

    @staticmethod
    def list_public_apis() -> QuerySet:
        return (
            API.objects.filter(
                visibility=API.Visibility.PUBLIC,
                lifecycle=API.Lifecycle.PUBLISHED,
                is_active=True,
            )
            .select_related(
                "organization",
                "created_by",
            )
        )

    @staticmethod
    def search_apis(keyword):
        return (
            API.objects.filter(
                Q(name__icontains=keyword) |
                Q(summary__icontains=keyword),
                is_active=True,
            )
            .select_related(
                "organization",
                "created_by",
            )
        )