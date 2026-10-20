
from django.contrib import admin
from django.utils.html import format_html

from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "price",
        "stock",
        "is_available",
        "image_thumbnail",
    )

    list_filter = ("is_available",)
    search_fields = ("name", "description", "slug")
    ordering = ("name",)
    list_per_page = 25
    save_on_top = True

    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("image_preview",)

    fields = (
        "name",
        "slug",
        "description",
        "price",
        "stock",
        "image",
        "image_preview",
        "is_available",
    )

    @admin.display(description="Image")
    def image_thumbnail(self, obj):
        if not obj.image:
            return "No image"

        try:
            return format_html(
                '<img src="{}" width="60" height="50" '
                'style="object-fit:contain;" alt="Product image" />',
                obj.image.url,
            )
        except (ValueError, OSError):
            return "Image unavailable"

    @admin.display(description="Image Preview")
    def image_preview(self, obj):
        if not obj or not obj.image:
            return "No image uploaded"

        try:
            return format_html(
                '<img src="{}" width="240" height="180" '
                'style="object-fit:contain;" alt="Product image" />',
                obj.image.url,
            )
        except (ValueError, OSError):
            return "Image unavailable"
