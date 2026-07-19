from django.db import transaction

from apps.apis.models import APIVersion


class APIVersionService:

    @staticmethod
    @transaction.atomic
    def create_version(
        *,
        api,
        version,
        title,
        description="",
        base_path="/",
        status=APIVersion.Status.DRAFT,
        is_default=False,
    ):

        if is_default:
            APIVersion.objects.filter(
                api=api,
                is_default=True,
            ).update(is_default=False)

        api_version = APIVersion.objects.create(
            api=api,
            version=version,
            title=title,
            description=description,
            base_path=base_path,
            status=status,
            is_default=is_default,
        )

        return api_version
    
    @staticmethod
    @transaction.atomic
    def update_version(
        *,
        version: APIVersion,
        title=None,
        description=None,
        base_path=None,
        status=None,
        is_default=None,
    ):

        if title is not None:
            version.title = title

        if description is not None:
            version.description = description

        if base_path is not None:
            version.base_path = base_path

        if status is not None:
            version.status = status

        if is_default is not None:
            if is_default:
                APIVersion.objects.filter(
                    api=version.api,
                    is_default=True,
                ).update(is_default=False)

            version.is_default = is_default

        version.save()

        return version
    
    @staticmethod
    @transaction.atomic
    def delete_version(
        *,
        version: APIVersion,
    ):

        version.delete()

        return True







    @staticmethod
    @transaction.atomic
    def set_default_version(
        *,
        version: APIVersion,
    ):

        APIVersion.objects.filter(
            api=version.api,
            is_default=True,
        ).update(is_default=False)

        version.is_default = True
        version.save()

        return version
    
    @staticmethod
    @transaction.atomic
    def activate_version(
        *,
        version: APIVersion,
    ):

        version.status = APIVersion.Status.ACTIVE
        version.save()

        return version
    
    @staticmethod
    @transaction.atomic
    def deactivate_version(
        *,
        version: APIVersion,
    ):

        version.status = APIVersion.Status.DEPRECATED
        version.save()

        return version
    
    @staticmethod
    @transaction.atomic
    def archive_version(
        *,
        version: APIVersion,
    ):

        version.status = APIVersion.Status.ARCHIVED
        version.save()

        return version
    

    @staticmethod
    @transaction.atomic
    def restore_version(
        *,
        version: APIVersion,
    ):

        version.status = APIVersion.Status.DRAFT
        version.save()

        return version
    

    @staticmethod
    @transaction.atomic
    def get_default_version(
        *,
        api,
    ):

        return APIVersion.objects.filter(
            api=api,
            is_default=True,
        ).first()
    

    @staticmethod
    @transaction.atomic
    def get_active_versions(
        *,
        api,
    ):

        return APIVersion.objects.filter(
            api=api,
            status=APIVersion.Status.ACTIVE,
        ).order_by("-created_at")
    

    @staticmethod
    @transaction.atomic
    def delete_versions(
        *,
        api,
    ):

        APIVersion.objects.filter(
            api=api,
        ).delete()

        return True