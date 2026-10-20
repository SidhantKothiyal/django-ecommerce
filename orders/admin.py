
from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    can_delete = False
    show_change_link = False

    fields = (
        "product",
        "product_name",
        "unit_price",
        "quantity",
    )

    readonly_fields = fields

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "full_name",
        "total_amount",
        "status",
        "payment_method",
        "payment_status",
        "created_at",
    )

    list_filter = (
        "status",
        "payment_method",
        "payment_status",
        "created_at",
    )

    search_fields = (
        "full_name",
        "email",
        "phone",
        "user__username",
    )

    # Only order status can be changed from the list page.
    list_editable = ("status",)

    list_per_page = 25
    date_hierarchy = "created_at"
    ordering = ("-created_at",)

    readonly_fields = (
        "user",
        "full_name",
        "email",
        "phone",
        "address_line1",
        "address_line2",
        "city",
        "state",
        "postal_code",
        "payment_method",
        "payment_status",
        "total_amount",
        "created_at",
        "updated_at",
    )

    inlines = (OrderItemInline,)
