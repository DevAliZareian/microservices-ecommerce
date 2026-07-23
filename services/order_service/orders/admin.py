from django.contrib import admin
from orders.models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['subtotal']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_id', 'status', 'total', 'created_at']
    list_filter = ['status']
    search_fields = ['user_id']
    inlines = [OrderItemInline]
    readonly_fields = ['created_at', 'updated_at']
