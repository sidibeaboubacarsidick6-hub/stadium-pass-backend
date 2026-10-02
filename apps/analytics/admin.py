from django.contrib import admin

from .models import MatchStatsSnapshot


@admin.register(MatchStatsSnapshot)
class MatchStatsSnapshotAdmin(admin.ModelAdmin):
    list_display = ('match', 'date', 'tickets_sold', 'revenue', 'tickets_scanned')
    list_filter = ('date', 'match__competition')
    search_fields = ('match__home_team__name', 'match__away_team__name')
    date_hierarchy = 'date'
