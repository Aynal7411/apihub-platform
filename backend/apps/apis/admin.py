from django.contrib import admin

from .models import API


@admin.register(API)
class APIAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "organization",
        "visibility",
        "lifecycle",
        "auth_type",
        "created_at",
    )

    search_fields = (
        "name",
        "slug",
    )

    list_filter = (
        "visibility",
        "lifecycle",
        "category",
    )

    prepopulated_fields = {
        "slug": ("name",)
    }


from .models import API, APIVersion

admin.site.register(APIVersion)   