from django.contrib import admin

from .models import Team, TeamStaff


class TeamStaffInline(admin.TabularInline):
    model = TeamStaff
    extra = 0
    fields = ('user', 'role', 'is_active')


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_name', 'city', 'is_active')
    list_filter = ('is_active', 'city')
    search_fields = ('name', 'short_name', 'city')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [TeamStaffInline]


@admin.register(TeamStaff)
class TeamStaffAdmin(admin.ModelAdmin):
    list_display = ('user', 'team', 'role', 'is_active')
    list_filter = ('role', 'is_active', 'team')
    search_fields = ('user__email', 'user__first_name', 'team__name')
