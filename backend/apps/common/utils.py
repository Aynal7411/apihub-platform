import secrets
import string


def generate_random_string(length=32):
    """
    Generate a secure random string.
    """
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))

from rest_framework.response import Response


def success_response(
    message="Success",
    data=None,
    status_code=200,
):
    """
    Standard success API response.
    """

    return Response(
        {
            "success": True,
            "message": message,
            "data": data,
        },
        status=status_code,
    )


def error_response(
    message="Something went wrong",
    errors=None,
    status_code=400,
):
    """
    Standard error API response.
    """

    return Response(
        {
            "success": False,
            "message": message,
            "errors": errors,
        },
        status=status_code,
    )