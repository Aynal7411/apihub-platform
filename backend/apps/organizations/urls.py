from django.urls import path

from apps.organizations.views.organization_view import (
    OrganizationDetailAPIView,
    OrganizationListCreateAPIView,
)

from apps.organizations.views.membership_view import (
    OrganizationMemberDetailAPIView,
    OrganizationMemberListCreateAPIView,
)

from apps.organizations.views.invitation_view import (
    AcceptOrganizationInvitationAPIView,
    OrganizationInvitationListCreateAPIView,
)
app_name = "organizations"

urlpatterns = [
    path(
        "",
        OrganizationListCreateAPIView.as_view(),
        name="organization-list-create",
    ),
    path(
        "<uuid:id>/",
        OrganizationDetailAPIView.as_view(),
        name="organization-detail",
    ),


    path(
    "<uuid:organization_id>/members/",
    OrganizationMemberListCreateAPIView.as_view(),
    name="organization-member-list-create",
),

path(
    "<uuid:organization_id>/members/<uuid:membership_id>/",
    OrganizationMemberDetailAPIView.as_view(),
    name="organization-member-detail",
),



path(
    "<uuid:organization_id>/invitations/",
    OrganizationInvitationListCreateAPIView.as_view(),
    name="organization-invitation-list-create",
),

path(
    "invitations/<uuid:token>/accept/",
    AcceptOrganizationInvitationAPIView.as_view(),
    name="organization-invitation-accept",
),
]