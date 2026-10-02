from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ('category', 'quantity', 'unit_price', 'subtotal')
    readonly_fields = ('subtotal',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_number', 'match', 'buyer_name', 'total',
        'status', 'created_at',
    )
    list_filter = ('status', 'match__competition')
    search_fields = ('order_number', 'guest_email', 'buyer__email')
    date_hierarchy = 'created_at'
    readonly_fields = ('uuid', 'order_number', 'access_token', 'created_at', 'updated_at')
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'category', 'quantity', 'subtotal')
    search_fields = ('order__order_number', 'category__name')
