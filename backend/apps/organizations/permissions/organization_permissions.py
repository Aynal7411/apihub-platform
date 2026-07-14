from rest_framework.permissions import BasePermission, SAFE_METHODS

from apps.organizations.models import OrganizationMembership


class IsOrganizationMember(BasePermission):
    """
    Any active organization member can access the organization.
    """

    message = "You are not an active member of this organization."

    def has_object_permission(self, request, view, obj):
        return OrganizationMembership.objects.filter(
            organization=obj,
            user=request.user,
            is_active=True,
        ).exists()


class OrganizationRolePermission(BasePermission):
    """
    GET/HEAD/OPTIONS:
        Any active member.

    PUT/PATCH:
        OWNER or ADMIN.

    DELETE:
        OWNER only.
    """

    message = "You do not have permission to perform this action."

    def has_object_permission(self, request, view, obj):
        try:
            membership = OrganizationMembership.objects.get(
                organization=obj,
                user=request.user,
                is_active=True,
            )
        except OrganizationMembership.DoesNotExist:
            return False

        if request.method in SAFE_METHODS:
            return True

        if request.method in ["PUT", "PATCH"]:
            return membership.role in {
                OrganizationMembership.Role.OWNER,
                OrganizationMembership.Role.ADMIN,
            }

        if request.method == "DELETE":
            return (
                membership.role
                == OrganizationMembership.Role.OWNER
            )

        return False
    

class CanManageOrganizationMembers(BasePermission):
    message = "You do not have permission to manage organization members."

    def has_permission(self, request, view):
        organization = view.get_organization()

        try:
            membership = OrganizationMembership.objects.get(
                organization=organization,
                user=request.user,
                is_active=True,
            )
        except OrganizationMembership.DoesNotExist:
            return False

        if request.method in SAFE_METHODS:
            return True

        return membership.role in {
            OrganizationMembership.Role.OWNER,
            OrganizationMembership.Role.ADMIN,
        }   