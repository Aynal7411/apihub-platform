from django.core.exceptions import ValidationError
import re


def validate_slug(value):
    """
    Validate slug format.
    """
    if not re.match(r"^[a-z0-9-]+$", value):
        raise ValidationError(
            "Only lowercase letters, numbers and hyphens are allowed."
        )