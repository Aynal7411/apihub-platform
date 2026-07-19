import uuid

from django.db import models

from .api import API


class APIVersion(models.Model):

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        ACTIVE = "ACTIVE", "Active"
        DEPRECATED = "DEPRECATED", "Deprecated"
        ARCHIVED = "ARCHIVED", "Archived"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    api = models.ForeignKey(
        API,
        on_delete=models.CASCADE,
        related_name="versions",
    )

    version = models.CharField(
        max_length=20,
    )

    title = models.CharField(
        max_length=150,
    )

    description = models.TextField(
        blank=True,
    )

    base_path = models.CharField(
        max_length=100,
        default="/",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )

    is_default = models.BooleanField(
        default=False,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        db_table = "api_versions"
        ordering = ["created_at"]
        unique_together = (
            "api",
            "version",
        )

    def __str__(self):
        return f"{self.api.name} ({self.version})"