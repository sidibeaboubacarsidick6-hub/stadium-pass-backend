from django.contrib import admin

from .models import TeamWallet, WalletTransaction


class WalletTransactionInline(admin.TabularInline):
    model = WalletTransaction
    extra = 0
    fields = ('type', 'amount', 'balance_after', 'description', 'reference', 'created_at')
    readonly_fields = ('created_at',)
    can_delete = False
    max_num = 0


@admin.register(TeamWallet)
class TeamWalletAdmin(admin.ModelAdmin):
    list_display = (
        'team', 'balance_available', 'balance_pending',
        'balance_withdrawn', 'is_frozen', 'preferred_payout_method',
    )
    list_filter = ('is_frozen', 'preferred_payout_method')
    search_fields = ('team__name', 'payout_phone')
    readonly_fields = (
        'balance_available', 'balance_pending', 'balance_withdrawn',
        'total_balance', 'created_at', 'updated_at',
    )
    inlines = [WalletTransactionInline]


@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = ('wallet', 'type', 'amount', 'balance_after', 'created_at')
    list_filter = ('type',)
    search_fields = ('wallet__team__name', 'reference', 'description')
    date_hierarchy = 'created_at'
    readonly_fields = (
        'wallet', 'type', 'amount', 'balance_after',
        'description', 'reference', 'created_at',
    )
