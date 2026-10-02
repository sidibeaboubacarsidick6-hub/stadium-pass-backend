from django.contrib import admin

from .models import NotificationLog


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = (
        'channel', 'kind', 'recipient_email',
        'recipient_phone', 'status', 'created_at',
    )
    list_filter = ('channel', 'kind', 'status')
    search_fields = ('recipient_email', 'recipient_phone', 'subject')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')
