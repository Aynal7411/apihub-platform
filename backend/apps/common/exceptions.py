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