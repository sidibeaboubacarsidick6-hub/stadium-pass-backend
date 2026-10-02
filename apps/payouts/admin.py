from django.contrib import admin

from .models import PayoutRequest


@admin.register(PayoutRequest)
class PayoutRequestAdmin(admin.ModelAdmin):
    list_display = (
        'reference', 'wallet', 'amount', 'payout_method',
        'status', 'created_at',
    )
    list_filter = ('status', 'payout_method')
    search_fields = ('reference', 'wallet__team__name', 'payout_phone')
    date_hierarchy = 'created_at'
    readonly_fields = (
        'uuid', 'reference', 'amount_net', 'created_at',
        'processed_at', 'completed_at', 'provider_token',
        'provider_transaction_id', 'provider_status',
        'retry_count', 'last_error',
    )
