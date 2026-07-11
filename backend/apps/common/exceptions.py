from rest_framework.exceptions import APIException


class APIHubException(Exception):
    """
    Base exception for APIHub.
    """

    pass

class InvalidCredentials(APIException):
    status_code = 401
    default_detail = "Invalid email or password."
    default_code = "invalid_credentials"


from rest_framework.views import exception_handler
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        return response

    # SimpleJWT invalid / expired / blacklisted token
    if isinstance(exc, (InvalidToken, TokenError)):
        return _build_auth_error_response(
            response=response,
            code="token_not_valid",
            message="Invalid or expired authentication token.",
        )

    # DRF authentication failure
    if isinstance(exc, AuthenticationFailed):
        return _build_auth_error_response(
            response=response,
            code="authentication_failed",
            message="Authentication failed.",
        )

    # Missing authentication credentials
    if isinstance(exc, NotAuthenticated):
        return _build_auth_error_response(
            response=response,
            code="not_authenticated",
            message="Authentication credentials were not provided.",
        )

    return response


def _build_auth_error_response(response, code, message):
    detail = response.data.get("detail", message)

    if isinstance(detail, list):
        detail = " ".join(str(item) for item in detail)

    response.data = {
        "success": False,
        "message": message,
        "errors": {
            "code": code,
            "detail": str(detail),
        },
    }

    return response   