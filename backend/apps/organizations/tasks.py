from celery import shared_task

from apps.organizations.models import OrganizationInvitation
from apps.organizations.services.invitation_email_service import (
    OrganizationInvitationEmailService,
)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={
        "max_retries": 3,
    },
)
def send_organization_invitation_email(
    self,
    invitation_id,
):
    invitation = (
        OrganizationInvitation.objects
        .select_related(
            "organization",
            "invited_by",
        )
        .get(id=invitation_id)
    )

    OrganizationInvitationEmailService.send_invitation_email(
        invitation=invitation,
    )