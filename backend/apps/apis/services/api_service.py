from django.db import transaction
from django.utils.text import slugify
from django.utils import timezone
from apps.apis.models import API


class APIService:

    @staticmethod
    def generate_unique_slug(organization, name):
        """
        Generate a unique slug within an organization.
        """

        base_slug = slugify(name)
        slug = base_slug

        counter = 2

        while API.objects.filter(
            organization=organization,
            slug=slug,
        ).exists():

            slug = f"{base_slug}-{counter}"
            counter += 1

        return slug

    @staticmethod
    @transaction.atomic
    def create_api(
        *,
        organization,
        created_by,
        name,
        summary,
        description="",
        category=API.Category.UTILITY,
        visibility=API.Visibility.PRIVATE,
        auth_type=API.AuthType.API_KEY,
        website="",
        docs_url="",
    ):

        slug = APIService.generate_unique_slug(
            organization,
            name,
        )

        api = API.objects.create(
            organization=organization,
            created_by=created_by,
            name=name,
            slug=slug,
            summary=summary,
            description=description,
            category=category,
            visibility=visibility,
            auth_type=auth_type,
            website=website,
            docs_url=docs_url,
        )

        return api
    
    @staticmethod
    @transaction.atomic
    def update_api(
        *,
        api,
        **data,
    ):
        """
        Update API information.
        """

        updatable_fields = [
            "name",
            "summary",
            "description",
            "category",
            "visibility",
            "lifecycle",
            "auth_type",
            "website",
            "docs_url",
        ]

        name_changed = (
            "name" in data
            and data["name"] != api.name
        )

        for field in updatable_fields:
            if field in data:
                setattr(api, field, data[field])

        if name_changed:
            api.slug = APIService.generate_unique_slug(
                api.organization,
                api.name,
            )

        api.save()

        return api
    
    @staticmethod
    @transaction.atomic
    def soft_delete_api(
        *,
        api,
        deleted_by,
    ):

        api.is_active = False
        api.deleted_at = timezone.now()
        api.deleted_by = deleted_by

        api.save(
            update_fields=[
                "is_active",
                "deleted_at",
                "deleted_by",
            ]
        )

        return api