from django.contrib import admin

from .models import ScanSession, ScanLog


class ScanLogInline(admin.TabularInline):
    model = ScanLog
    extra = 0
    fields = ('result', 'ticket', 'scanned_at')
    readonly_fields = ('result', 'ticket', 'scanned_at')
    can_delete = False
    max_num = 0


@admin.register(ScanSession)
class ScanSessionAdmin(admin.ModelAdmin):
    list_display = (
        'agent', 'match', 'gate', 'started_at',
        'total_scanned', 'total_valid', 'total_rejected',
    )
    list_filter = ('match', 'gate')
    search_fields = ('agent__email', 'match__home_team__name')
    date_hierarchy = 'started_at'
    readonly_fields = ('started_at',)
    inlines = [ScanLogInline]


@admin.register(ScanLog)
class ScanLogAdmin(admin.ModelAdmin):
    list_display = ('session', 'result', 'ticket', 'scanned_at')
    list_filter = ('result', 'scanned_at')
    search_fields = ('ticket__ticket_number', 'qr_token_received')
    date_hierarchy = 'scanned_at'
    readonly_fields = ('session', 'ticket', 'qr_token_received', 'result', 'scanned_at', 'client_uuid')
