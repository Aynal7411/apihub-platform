from django.conf import settings
from django.db import models
from django.utils.text import slugify
import uuid

from apps.organizations.models import Organization


class API(models.Model):

    class Visibility(models.TextChoices):
        PUBLIC = "PUBLIC", "Public"
        PRIVATE = "PRIVATE", "Private"
        UNLISTED = "UNLISTED", "Unlisted"

    class Lifecycle(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        PUBLISHED = "PUBLISHED", "Published"
        DEPRECATED = "DEPRECATED", "Deprecated"
        ARCHIVED = "ARCHIVED", "Archived"

    class AuthType(models.TextChoices):
        NONE = "NONE", "None"
        API_KEY = "API_KEY", "API Key"
        JWT = "JWT", "JWT"
        OAUTH2 = "OAUTH2", "OAuth2"

    class Category(models.TextChoices):
        AI = "AI", "AI"
        PAYMENT = "PAYMENT", "Payment"
        WEATHER = "WEATHER", "Weather"
        FINANCE = "FINANCE", "Finance"
        HEALTHCARE = "HEALTHCARE", "Healthcare"
        DEVELOPER = "DEVELOPER", "Developer Tools"
        UTILITY = "UTILITY", "Utility"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="apis",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_apis",
    )

    name = models.CharField(max_length=150)

    slug = models.SlugField(max_length=170)

    summary = models.CharField(max_length=255)

    description = models.TextField(blank=True)

    category = models.CharField(
        max_length=30,
        choices=Category.choices,
        default=Category.UTILITY,
    )

    visibility = models.CharField(
        max_length=20,
        choices=Visibility.choices,
        default=Visibility.PRIVATE,
    )

    lifecycle = models.CharField(
        max_length=20,
        choices=Lifecycle.choices,
        default=Lifecycle.DRAFT,
    )

    auth_type = models.CharField(
        max_length=20,
        choices=AuthType.choices,
        default=AuthType.API_KEY,
    )

    website = models.URLField(blank=True)

    docs_url = models.URLField(blank=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    deleted_at = models.DateTimeField(
     null=True,
     blank=True,
)

    deleted_by = models.ForeignKey(
     settings.AUTH_USER_MODEL,
     blank=True,
     null=True,
     on_delete=models.SET_NULL,
     related_name="deleted_apis",
    )

    class Meta:
        db_table = "apis"
        ordering = ["-created_at"]
        unique_together = ("organization", "slug")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name