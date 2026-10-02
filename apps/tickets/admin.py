from django.contrib import admin

from .models import TicketCategory, Ticket


@admin.register(TicketCategory)
class TicketCategoryAdmin(admin.ModelAdmin):
    list_display = (
        'match', 'name', 'price', 'total_quantity',
        'quantity_sold', 'remaining', 'is_active',
    )
    list_filter = ('is_active', 'match__competition')
    search_fields = ('name', 'match__home_team__name', 'match__away_team__name')
    readonly_fields = ('quantity_sold',)

    def remaining(self, obj):
        return obj.remaining
    remaining.short_description = "Restants"


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = (
        'ticket_number', 'category', 'status',
        'holder_name', 'created_at', 'scanned_count',
    )
    list_filter = ('status', 'category__match')
    search_fields = ('ticket_number', 'holder_name', 'holder_email')
    readonly_fields = (
        'uuid', 'ticket_number', 'qr_token',
        'first_scanned_at', 'scanned_count',
        'created_at', 'updated_at',
    )
    date_hierarchy = 'created_at'
