from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from apps.common.models import BaseModel
from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin, BaseModel):
    """
    Custom User model for APIHub.
    """

    email = models.EmailField(
        unique=True,
        db_index=True,
    )

    username = models.CharField(
        max_length=150,
        unique=True,
    )

    first_name = models.CharField(
        max_length=150,
        blank=True,
    )

    last_name = models.CharField(
        max_length=150,
        blank=True,
    )

    phone_number = models.CharField(
        max_length=20,
        blank=True,
    )

    avatar = models.ImageField(
        upload_to="avatars/",
        blank=True,
        null=True,
    )

    bio = models.TextField(
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    is_staff = models.BooleanField(
        default=False,
    )

    is_verified = models.BooleanField(
        default=False,
    )

    objects = UserManager()

    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = ["username"]

    class Meta:
        db_table = "users"
        ordering = ["-created_at"]
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        """
        Return the user's full name.
        """
        return f"{self.first_name} {self.last_name}".strip()