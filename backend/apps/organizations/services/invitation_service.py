from datetime import timedelta

from django.db import transaction

from apps.organizations.tasks import (
    send_organization_invitation_email,
)
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.organizations.models import (
    OrganizationInvitation,
    OrganizationMembership,
)


class OrganizationInvitationService:

    @staticmethod
    @transaction.atomic
    def create_invitation(
        *,
        organization,
        email,
        role,
        invited_by,
    ):
        email = email.strip().lower()

        if OrganizationMembership.objects.filter(
            organization=organization,
            user__email__iexact=email,
            is_active=True,
        ).exists():
            raise ValidationError(
                {"email": "This user is already an organization member."}
            )

        pending_invitation = (
            OrganizationInvitation.objects
            .filter(
                organization=organization,
                email__iexact=email,
                status=OrganizationInvitation.Status.PENDING,
            )
            .first()
        )

        if pending_invitation:
            if not pending_invitation.is_expired:
                raise ValidationError(
                    {
                        "email":
                        "A pending invitation already exists for this email."
                    }
                )

            pending_invitation.status = (
                OrganizationInvitation.Status.REVOKED
            )
            pending_invitation.save(
                update_fields=["status"]
            )

        invitation = OrganizationInvitation.objects.create(
        organization=organization,
        email=email,
        role=role,
        invited_by=invited_by,
        expires_at=timezone.now() + timedelta(days=7),
)

        transaction.on_commit(
    lambda: send_organization_invitation_email.delay(
        str(invitation.id)
    )
)

        return invitation
    

    @staticmethod
    @transaction.atomic
    def accept_invitation(*, invitation, user):

        if (
            invitation.status
            != OrganizationInvitation.Status.PENDING
        ):
            raise ValidationError(
                "This invitation is no longer active."
            )

        if invitation.is_expired:
            invitation.status = (
                OrganizationInvitation.Status.REVOKED
            )
            invitation.save(
                update_fields=["status"]
            )

            raise ValidationError(
                "This invitation has expired."
            )

        if user.email.lower() != invitation.email.lower():
            raise ValidationError(
                "This invitation belongs to another email address."
            )

        membership, created = (
            OrganizationMembership.objects.get_or_create(
                organization=invitation.organization,
                user=user,
                defaults={
                    "role": invitation.role,
                    "is_active": True,
                },
            )
        )

        if not created:
            if membership.is_active:
                raise ValidationError(
                    "You are already a member of this organization."
                )

            membership.role = invitation.role
            membership.is_active = True
            membership.save(
                update_fields=[
                    "role",
                    "is_active",
                ]
            )

        invitation.status = (
            OrganizationInvitation.Status.ACCEPTED
        )
        invitation.accepted_at = timezone.now()

        invitation.save(
            update_fields=[
                "status",
                "accepted_at",
            ]
        )

        return membership