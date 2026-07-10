from django.db import models

class BaseManager(models.Manager):
    """
    A base manager that provides common query methods for all models.
    """

    def get_queryset(self):
        """
        Override the default queryset to include only active records.
        """
        return super().get_queryset().filter(is_active=True)
    
class SoftDeleteManager(BaseManager):   
      """
       Returns only non-deleted objects.
      """
      def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)