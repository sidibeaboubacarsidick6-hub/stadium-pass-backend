from django.contrib import admin

from apps.tickets.models import TicketCategory

from .models import Match


class TicketCategoryInline(admin.TabularInline):
    """Catégories de billets rattachées au match."""
    model = TicketCategory
    extra = 0
    fields = (
        'order', 'name', 'price', 'total_quantity',
        'quantity_sold', 'gate', 'block_label', 'is_active',
    )
    readonly_fields = ('quantity_sold',)
    ordering = ('order', 'price')
    verbose_name = "Catégorie de billets"
    verbose_name_plural = "Catégories de billets"


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = (
        'home_team', 'away_team', 'competition',
        'kickoff_at', 'venue', 'status',
    )
    list_filter = ('status', 'competition', 'venue', 'home_team')
    search_fields = ('home_team__name', 'away_team__name', 'competition__name')
    date_hierarchy = 'kickoff_at'
    readonly_fields = ('uuid', 'created_at', 'updated_at')

    fieldsets = (
        ('Organisation', {
            'fields': ('competition', 'season', 'match_day')
        }),
        ('Équipes', {
            'fields': ('home_team', 'away_team')
        }),
        ('Lieu et date', {
            'fields': ('venue', 'kickoff_at')
        }),
        ('Vente', {
            'fields': ('sale_start_at', 'sale_end_at', 'away_quota_percent')
        }),
        ('Statut', {
            'fields': ('status',)
        }),
        ('Médias', {
            'fields': ('poster', 'tv_channel', 'description')
        }),
        ('Système', {
            'fields': ('uuid', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    inlines = [TicketCategoryInline]
