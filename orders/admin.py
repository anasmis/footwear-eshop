from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "product_name", "price", "quantity", "subtotal")

    def subtotal(self, obj):
        return obj.subtotal


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "full_name", "status", "total", "created_at")
    list_filter = ("status", "created_at")
    list_editable = ("status",)
    search_fields = ("user__username", "full_name", "phone")
    date_hierarchy = "created_at"
    inlines = [OrderItemInline]

    @admin.display(description="Total")
    def total(self, obj):
        return f"{obj.total} MAD"
