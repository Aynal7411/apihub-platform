import uuid
from django.db import models


# Create your models here.

class UUIDModel(models.Model):
    """
    An abstract base class model that provides a UUID primary key field.
    """

    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False 
    )

    class Meta:
        abstract = True

class TimeStampedModel(models.Model):
    """
    An abstract base class model that provides self-updating 'created' and 'modified' fields.
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class SoftDeleteModel(models.Model):
    """
    Abstract model for soft deletion.
    """

    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True


class BaseModel(UUIDModel, TimeStampedModel, SoftDeleteModel):
    """
    Base model for all application models.

    Includes:
    - UUID primary key
    - created_at
    - updated_at
    """

    class Meta:
        abstract = True



