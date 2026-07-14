from django.conf import settings
from django.core.mail import send_mail


class OrganizationInvitationEmailService:

    @staticmethod
    def send_invitation_email(*, invitation):
        frontend_url = getattr(
            settings,
            "FRONTEND_URL",
            "http://localhost:3000",
        )

        accept_url = (
            f"{frontend_url}/invitations/"
            f"{invitation.token}/accept"
        )

        subject = (
            f"You're invited to join "
            f"{invitation.organization.name}"
        )

        message = (
            f"You have been invited to join "
            f"{invitation.organization.name}.\n\n"
            f"Role: {invitation.get_role_display()}\n"
            f"Invited by: {invitation.invited_by.email}\n\n"
            f"Accept invitation:\n{accept_url}\n\n"
            f"This invitation expires at "
            f"{invitation.expires_at}."
        )

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[invitation.email],
            fail_silently=False,
        )