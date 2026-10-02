from django.contrib import admin

from .models import Venue, Gate


class GateInline(admin.TabularInline):
    model = Gate
    extra = 1
    fields = ('code', 'name', 'zone', 'capacity_per_hour', 'is_active')


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'capacity', 'is_active')
    list_filter = ('is_active', 'city')
    search_fields = ('name', 'city', 'address')
    inlines = [GateInline]


@admin.register(Gate)
class GateAdmin(admin.ModelAdmin):
    list_display = ('venue', 'code', 'name', 'zone', 'is_active')
    list_filter = ('venue', 'is_active')
    search_fields = ('name', 'code', 'zone')
