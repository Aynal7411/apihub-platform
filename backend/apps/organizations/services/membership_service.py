from django.db import transaction
from rest_framework.exceptions import ValidationError

from apps.organizations.models import OrganizationMembership


class OrganizationMembershipService:

    @staticmethod
    @transaction.atomic
    def add_member(*, organization, user, role):
        if OrganizationMembership.objects.filter(
            organization=organization,
            user=user,
        ).exists():
            raise ValidationError(
                {"email": "User is already a member of this organization."}
            )

        return OrganizationMembership.objects.create(
            organization=organization,
            user=user,
            role=role,
        )

    @staticmethod
    @transaction.atomic
    def update_role(*, membership, role):
        if membership.role == OrganizationMembership.Role.OWNER:
            raise ValidationError(
                "The organization owner's role cannot be changed."
            )

        membership.role = role
        membership.save(
            update_fields=["role"]
        )

        return membership

    @staticmethod
    @transaction.atomic
    def remove_member(*, membership):
        if membership.role == OrganizationMembership.Role.OWNER:
            raise ValidationError(
                "The organization owner cannot be removed."
            )

        membership.delete()