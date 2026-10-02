from django.contrib import admin

from .models import Competition, Season, MatchDay


class SeasonInline(admin.TabularInline):
    model = Season
    extra = 0
    fields = ('name', 'start_date', 'end_date', 'is_current', 'is_active')


@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'is_active')
    list_filter = ('type', 'is_active')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    inlines = [SeasonInline]


class MatchDayInline(admin.TabularInline):
    model = MatchDay
    extra = 0
    fields = ('number', 'name', 'start_date', 'end_date')


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ('competition', 'name', 'start_date', 'end_date', 'is_current')
    list_filter = ('competition', 'is_current', 'is_active')
    search_fields = ('competition__name', 'name')
    inlines = [MatchDayInline]


@admin.register(MatchDay)
class MatchDayAdmin(admin.ModelAdmin):
    list_display = ('season', 'number', 'name', 'start_date', 'end_date')
    list_filter = ('season__competition',)
    search_fields = ('season__name', 'name')
