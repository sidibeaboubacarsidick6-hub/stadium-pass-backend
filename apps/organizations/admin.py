"""Stadium Pass — Admin organisations."""
from django.contrib import admin

from .models import Organization


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "owner", "city", "is_active", "created_at")
    list_filter = ("is_active", "city")
    search_fields = ("name", "slug", "owner__email", "owner__first_name", "owner__last_name")
    readonly_fields = ("slug", "created_at", "updated_at")
    autocomplete_fields = ("owner",)

    fieldsets = (
        ("Identité", {
            "fields": ("name", "slug", "owner", "is_active"),
        }),
        ("Contact", {
            "fields": ("email", "phone", "address", "city"),
        }),
        ("Branding", {
            "fields": ("logo_url", "description"),
        }),
        ("Métadonnées", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )
