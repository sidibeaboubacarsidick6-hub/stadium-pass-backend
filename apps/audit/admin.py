from django.contrib import admin

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'action', 'user', 'description_preview')
    list_filter = ('action', 'created_at')
    search_fields = ('description', 'user__email', 'object_id')
    date_hierarchy = 'created_at'
    readonly_fields = (
        'user', 'action', 'description', 'model_name',
        'object_id', 'metadata', 'ip_address', 'user_agent',
        'created_at', 'updated_at',
    )

    def description_preview(self, obj):
        return obj.description[:80] + ('…' if len(obj.description) > 80 else '')
    description_preview.short_description = "Description"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
