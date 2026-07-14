from django.db import transaction
from django.utils.text import slugify

from apps.organizations.models import (
    Organization,
    OrganizationMembership,
)


class OrganizationService:

    @staticmethod
    @transaction.atomic
    def create_organization(*, user, name, description=""):
        """
        Create an organization and assign the creator
        as the organization owner.
        """

        base_slug = slugify(name)
        slug = base_slug
        counter = 1

        while Organization.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        organization = Organization.objects.create(
            name=name,
            slug=slug,
            description=description,
            owner=user,
        )

        OrganizationMembership.objects.create(
            organization=organization,
            user=user,
            role=OrganizationMembership.Role.OWNER,
        )

        return organization
    
    @staticmethod
    @transaction.atomic
    def update_organization(
        *,
        organization,
        name=None,
        description=None,
    ):
        if name is not None:
            organization.name = name

        if description is not None:
            organization.description = description

        organization.save()

        return organization


    @staticmethod
    @transaction.atomic
    def deactivate_organization(*, organization):
        """
        Soft delete an organization.
        """

        organization.is_active = False

        organization.save(
            update_fields=[
                "is_active",
                "updated_at",
            ]
        )

        return organization 