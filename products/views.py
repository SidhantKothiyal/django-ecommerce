
"""
Views for Shopora product catalogue and shopping cart.
"""

from decimal import Decimal

from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .cart import (
    add_to_cart,
    get_cart_items,
    remove_from_cart,
    update_cart,
)
from .forms import ProductSearchForm
from .models import Product


def product_list(request):
    """Display available products and support catalogue search."""
    products = Product.objects.filter(is_available=True)
    form = ProductSearchForm(request.GET or None)

    if form.is_valid():
        query = form.cleaned_data.get("q", "").strip()

        if query:
            products = products.filter(
                Q(name__icontains=query)
                | Q(description__icontains=query)
            )

    return render(
        request,
        "products/product_list.html",
        {
            "products": products,
            "form": form,
        },
    )


def product_detail(request, slug):
    """Display an available product's details using its slug."""
    product = get_object_or_404(
        Product,
        slug=slug,
        is_available=True,
    )

    return render(
        request,
        "products/product_detail.html",
        {"product": product},
    )


def cart_detail(request):
    """Display cart items and calculate their total."""
    items = get_cart_items(request)

    total = sum(
        (item["subtotal"] for item in items),
        Decimal("0.00"),
    )

    return render(
        request,
        "products/cart.html",
        {
            "items": items,
            "total": total,
        },
    )


@require_POST
def cart_add(request, product_id):
    """Add a product to the session cart."""
    product = get_object_or_404(
        Product,
        pk=product_id,
        is_available=True,
    )

    try:
        quantity = int(request.POST.get("quantity", "1"))

        if quantity < 1:
            raise ValueError("Quantity must be positive.")

        add_to_cart(request, product, quantity)

    except (ValueError, TypeError, OverflowError):
        messages.error(
            request,
            "Invalid quantity or insufficient available stock.",
        )
    else:
        messages.success(
            request,
            f"{product.name} added to your cart.",
        )

    return redirect("cart_detail")


@require_POST
def cart_update(request, product_id):
    """Update a cart item's quantity or remove it when quantity is zero."""
    product = get_object_or_404(
        Product,
        pk=product_id,
    )

    try:
        quantity = int(request.POST.get("quantity", "1"))

        if quantity < 0:
            raise ValueError("Quantity cannot be negative.")

        if quantity == 0:
            remove_from_cart(request, product)

            messages.success(
                request,
                f"{product.name} removed from your cart.",
            )
        else:
            update_cart(request, product, quantity)

            messages.success(
                request,
                "Cart updated successfully.",
            )

    except (ValueError, TypeError, OverflowError):
        messages.error(
            request,
            "Invalid quantity or insufficient available stock.",
        )

    return redirect("cart_detail")


@require_POST
def cart_remove(request, product_id):
    """Remove a product from the cart."""
    product = get_object_or_404(
        Product,
        pk=product_id,
    )

    remove_from_cart(request, product)

    messages.success(
        request,
        f"{product.name} removed from your cart.",
    )

    return redirect("cart_detail")
