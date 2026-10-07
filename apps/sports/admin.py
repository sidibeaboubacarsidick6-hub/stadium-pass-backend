from django.contrib import admin

from .models import Sport


@admin.register(Sport)
class SportAdmin(admin.ModelAdmin):
    list_display = ("name", "kind", "display_order", "is_active", "updated_at")
    list_filter = ("kind", "is_active")
    search_fields = ("name", "slug")
    readonly_fields = ("slug", "created_at", "updated_at")
    ordering = ("display_order", "name")

    fieldsets = (
        ("Identité", {
            "fields": ("name", "slug", "kind", "description"),
        }),
        ("Configuration", {
            "fields": ("rules", "display_order", "is_active"),
        }),
        ("Métadonnées", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )
