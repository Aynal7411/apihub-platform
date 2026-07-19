import uuid

from django.db import models

from .api_version import APIVersion


class APIEndpoint(models.Model):

    class HttpMethod(models.TextChoices):
        GET = "GET", "GET"
        POST = "POST", "POST"
        PUT = "PUT", "PUT"
        PATCH = "PATCH", "PATCH"
        DELETE = "DELETE", "DELETE"

    class Authentication(models.TextChoices):
        NONE = "NONE", "None"
        API_KEY = "API_KEY", "API Key"
        JWT = "JWT", "JWT"
        OAUTH2 = "OAUTH2", "OAuth2"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    version = models.ForeignKey(
        APIVersion,
        on_delete=models.CASCADE,
        related_name="endpoints",
    )

    name = models.CharField(
        max_length=150,
    )

    path = models.CharField(
        max_length=255,
    )

    method = models.CharField(
        max_length=10,
        choices=HttpMethod.choices,
    )

    summary = models.CharField(
        max_length=255,
        blank=True,
    )

    description = models.TextField(
        blank=True,
    )

    authentication = models.CharField(
        max_length=20,
        choices=Authentication.choices,
        default=Authentication.API_KEY,
    )

    rate_limit = models.PositiveIntegerField(
        default=1000,
        help_text="Requests per hour",
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        db_table = "api_endpoints"
        ordering = ["path", "method"]
        unique_together = (
            "version",
            "path",
            "method",
        )

    def __str__(self):
        return f"{self.method} {self.path}"