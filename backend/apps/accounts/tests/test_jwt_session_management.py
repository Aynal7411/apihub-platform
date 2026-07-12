from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import (
    OutstandingToken,
    BlacklistedToken,
)


User = get_user_model()


class JWTSessionManagementTestCase(APITestCase):
    """
    Sprint 3.2.7.10
    JWT Session Visibility & Active Device Management.

    Security guarantees tested:
    - Authentication is required.
    - Users can view only their own active sessions.
    - Blacklisted/revoked sessions are excluded.
    - Users can revoke one specific session.
    - Users cannot revoke another user's session.
    - Revoked refresh tokens cannot be reused.
    - Nonexistent sessions are handled safely.
    - Already-revoked sessions are handled safely.
    - API responses follow the standardized response contract.
    """

    def setUp(self):
        self.sessions_url = reverse("accounts:sessions")

        self.user = User.objects.create_user(
            username="session_user",
            email="sessions@example.com",
            password="StrongPassword123!",
        )

        self.other_user = User.objects.create_user(
            username="other_session_user",
            email="other-sessions@example.com",
            password="StrongPassword123!",
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def create_token_pair(self, user):
        """
        Create a fresh refresh/access token pair.

        RefreshToken.for_user() also creates an OutstandingToken record
        when the SimpleJWT blacklist application is enabled.
        """
        refresh = RefreshToken.for_user(user)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "jti": refresh["jti"],
        }

    def authenticate(self, access_token):
        """
        Authenticate subsequent requests using a JWT access token.
        """
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {access_token}"
        )

    def get_outstanding_token(self, jti):
        """
        Return the OutstandingToken associated with the supplied JTI.
        """
        return OutstandingToken.objects.get(jti=jti)

    def get_session_revoke_url(self, session_id):
        """
        Build the URL used to revoke one specific session.
        """
        return reverse(
            "accounts:session-revoke",
            kwargs={"session_id": session_id},
        )

    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------

    def test_session_list_requires_authentication(self):
        """
        Anonymous users must not be able to inspect active sessions.
        """
        response = self.client.get(self.sessions_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_session_revoke_requires_authentication(self):
        """
        Anonymous users must not be able to revoke sessions.
        """
        token_pair = self.create_token_pair(self.user)

        outstanding_token = self.get_outstanding_token(
            token_pair["jti"]
        )

        url = self.get_session_revoke_url(
            outstanding_token.id
        )

        response = self.client.delete(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    # ------------------------------------------------------------------
    # Active session listing
    # ------------------------------------------------------------------

    def test_authenticated_user_can_list_active_sessions(self):
        """
        An authenticated user should be able to retrieve
        their active JWT sessions.
        """
        session = self.create_token_pair(self.user)

        self.authenticate(session["access"])

        response = self.client.get(self.sessions_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertTrue(response.data["success"])

    def test_session_list_contains_all_active_user_sessions(self):
        """
        All non-blacklisted outstanding tokens belonging to the
        authenticated user should appear in the session list.
        """
        first_session = self.create_token_pair(self.user)
        second_session = self.create_token_pair(self.user)
        third_session = self.create_token_pair(self.user)

        self.authenticate(first_session["access"])

        response = self.client.get(self.sessions_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        sessions = response.data["data"]["sessions"]

        returned_jtis = {
            session["jti"]
            for session in sessions
        }

        self.assertIn(
            first_session["jti"],
            returned_jtis,
        )

        self.assertIn(
            second_session["jti"],
            returned_jtis,
        )

        self.assertIn(
            third_session["jti"],
            returned_jtis,
        )

    # ------------------------------------------------------------------
    # Session ownership isolation
    # ------------------------------------------------------------------

    def test_session_list_does_not_expose_other_users_sessions(self):
        """
        A user must never see another user's JWT sessions.
        """
        user_session = self.create_token_pair(self.user)
        other_user_session = self.create_token_pair(
            self.other_user
        )

        self.authenticate(user_session["access"])

        response = self.client.get(self.sessions_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        sessions = response.data["data"]["sessions"]

        returned_jtis = {
            session["jti"]
            for session in sessions
        }

        self.assertIn(
            user_session["jti"],
            returned_jtis,
        )

        self.assertNotIn(
            other_user_session["jti"],
            returned_jtis,
        )

    # ------------------------------------------------------------------
    # Revoked session filtering
    # ------------------------------------------------------------------

    def test_blacklisted_sessions_are_excluded_from_active_sessions(self):
        """
        Revoked refresh-token sessions must not appear in the
        active session list.
        """
        active_session = self.create_token_pair(self.user)
        revoked_session = self.create_token_pair(self.user)

        RefreshToken(
            revoked_session["refresh"]
        ).blacklist()

        self.authenticate(active_session["access"])

        response = self.client.get(self.sessions_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        sessions = response.data["data"]["sessions"]

        returned_jtis = {
            session["jti"]
            for session in sessions
        }

        self.assertIn(
            active_session["jti"],
            returned_jtis,
        )

        self.assertNotIn(
            revoked_session["jti"],
            returned_jtis,
        )

    # ------------------------------------------------------------------
    # Session response data
    # ------------------------------------------------------------------

    def test_session_data_contains_required_fields(self):
        """
        Each session entry must expose the minimum safe metadata
        required for session management.

        Raw JWT values must never be exposed.
        """
        session = self.create_token_pair(self.user)

        self.authenticate(session["access"])

        response = self.client.get(self.sessions_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        sessions = response.data["data"]["sessions"]

        self.assertGreaterEqual(len(sessions), 1)

        session_data = sessions[0]

        self.assertIn("id", session_data)
        self.assertIn("jti", session_data)
        self.assertIn("created_at", session_data)
        self.assertIn("expires_at", session_data)

        self.assertNotIn(
            "token",
            session_data,
        )

        self.assertNotIn(
            "refresh",
            session_data,
        )

        self.assertNotIn(
            "access",
            session_data,
        )

    # ------------------------------------------------------------------
    # Specific session revocation
    # ------------------------------------------------------------------

    def test_authenticated_user_can_revoke_own_session(self):
        """
        A user should be able to revoke one specific session
        belonging to their account.
        """
        authentication_session = self.create_token_pair(
            self.user
        )

        target_session = self.create_token_pair(
            self.user
        )

        target_token = self.get_outstanding_token(
            target_session["jti"]
        )

        self.authenticate(
            authentication_session["access"]
        )

        url = self.get_session_revoke_url(
            target_token.id
        )

        response = self.client.delete(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertTrue(response.data["success"])

        self.assertTrue(
            BlacklistedToken.objects.filter(
                token=target_token
            ).exists()
        )

    def test_revoking_one_session_does_not_revoke_other_sessions(self):
        """
        Revoking one session must not affect another active session
        belonging to the same user.
        """
        first_session = self.create_token_pair(self.user)
        second_session = self.create_token_pair(self.user)

        second_token = self.get_outstanding_token(
            second_session["jti"]
        )

        self.authenticate(first_session["access"])

        url = self.get_session_revoke_url(
            second_token.id
        )

        response = self.client.delete(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        first_token = self.get_outstanding_token(
            first_session["jti"]
        )

        self.assertFalse(
            BlacklistedToken.objects.filter(
                token=first_token
            ).exists()
        )

        self.assertTrue(
            BlacklistedToken.objects.filter(
                token=second_token
            ).exists()
        )

    # ------------------------------------------------------------------
    # Ownership protection
    # ------------------------------------------------------------------

    def test_user_cannot_revoke_another_users_session(self):
        """
        A user must not be able to revoke a session owned
        by another user.

        Returning 404 avoids leaking whether another user's
        session identifier exists.
        """
        user_session = self.create_token_pair(self.user)

        other_user_session = self.create_token_pair(
            self.other_user
        )

        other_user_token = self.get_outstanding_token(
            other_user_session["jti"]
        )

        self.authenticate(user_session["access"])

        url = self.get_session_revoke_url(
            other_user_token.id
        )

        response = self.client.delete(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        self.assertFalse(
            BlacklistedToken.objects.filter(
                token=other_user_token
            ).exists()
        )

    # ------------------------------------------------------------------
    # Revoked token reuse prevention
    # ------------------------------------------------------------------

    def test_revoked_session_refresh_token_cannot_be_reused(self):
        """
        Once a session is revoked, its refresh token must not
        generate another access token.
        """
        authentication_session = self.create_token_pair(
            self.user
        )

        target_session = self.create_token_pair(
            self.user
        )

        target_token = self.get_outstanding_token(
            target_session["jti"]
        )

        self.authenticate(
            authentication_session["access"]
        )

        url = self.get_session_revoke_url(
            target_token.id
        )

        revoke_response = self.client.delete(url)

        self.assertEqual(
            revoke_response.status_code,
            status.HTTP_200_OK,
        )

        # Refresh endpoint is public.
        self.client.credentials()

        refresh_url = reverse(
            "accounts:token-refresh"
        )

        refresh_response = self.client.post(
            refresh_url,
            {
                "refresh": target_session["refresh"],
            },
            format="json",
        )

        self.assertIn(
            refresh_response.status_code,
            (
                status.HTTP_400_BAD_REQUEST,
                status.HTTP_401_UNAUTHORIZED,
            ),
        )

    # ------------------------------------------------------------------
    # Invalid and nonexistent sessions
    # ------------------------------------------------------------------

    def test_nonexistent_session_returns_404(self):
        """
        Revoking a nonexistent session must return a safe 404 response.
        """
        session = self.create_token_pair(self.user)

        self.authenticate(session["access"])

        url = self.get_session_revoke_url(
            999999999
        )

        response = self.client.delete(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    # ------------------------------------------------------------------
    # Already revoked session
    # ------------------------------------------------------------------

    def test_already_revoked_session_is_handled_safely(self):
        """
        Repeated revocation attempts must not create duplicate
        blacklist records or cause server errors.

        This endpoint is intentionally idempotent.
        """
        authentication_session = self.create_token_pair(
            self.user
        )

        target_session = self.create_token_pair(
            self.user
        )

        target_token = self.get_outstanding_token(
            target_session["jti"]
        )

        self.authenticate(
            authentication_session["access"]
        )

        url = self.get_session_revoke_url(
            target_token.id
        )

        first_response = self.client.delete(url)

        self.assertEqual(
            first_response.status_code,
            status.HTTP_200_OK,
        )

        blacklist_count_after_first_request = (
            BlacklistedToken.objects.filter(
                token=target_token
            ).count()
        )

        second_response = self.client.delete(url)

        self.assertEqual(
            second_response.status_code,
            status.HTTP_200_OK,
        )

        blacklist_count_after_second_request = (
            BlacklistedToken.objects.filter(
                token=target_token
            ).count()
        )

        self.assertEqual(
            blacklist_count_after_first_request,
            blacklist_count_after_second_request,
        )

        self.assertEqual(
            blacklist_count_after_second_request,
            1,
        )

    # ------------------------------------------------------------------
    # Standardized API response
    # ------------------------------------------------------------------

    def test_session_list_returns_standard_response_structure(self):
        """
        Session-list responses must follow the project's
        standardized success response contract.
        """
        session = self.create_token_pair(self.user)

        self.authenticate(session["access"])

        response = self.client.get(self.sessions_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn("success", response.data)
        self.assertIn("message", response.data)
        self.assertIn("data", response.data)

        self.assertTrue(response.data["success"])

        self.assertEqual(
            response.data["message"],
            "Active sessions retrieved successfully.",
        )

        self.assertIsInstance(
            response.data["data"],
            dict,
        )

        self.assertIn(
            "sessions",
            response.data["data"],
        )

        self.assertIsInstance(
            response.data["data"]["sessions"],
            list,
        )

    def test_session_revoke_returns_standard_response_structure(self):
        """
        Successful session-revocation responses must follow
        the standardized API response contract.
        """
        authentication_session = self.create_token_pair(
            self.user
        )

        target_session = self.create_token_pair(
            self.user
        )

        target_token = self.get_outstanding_token(
            target_session["jti"]
        )

        self.authenticate(
            authentication_session["access"]
        )

        url = self.get_session_revoke_url(
            target_token.id
        )

        response = self.client.delete(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn("success", response.data)
        self.assertIn("message", response.data)
        self.assertIn("data", response.data)

        self.assertTrue(response.data["success"])

        self.assertEqual(
            response.data["message"],
            "Session revoked successfully.",
        )