
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from products.models import Product

from .forms import CheckoutForm
from .models import Order, OrderItem


class CheckoutError(Exception):
    """Raised when checkout validation fails."""


def get_cart_items(cart):
    """Validate cart data and return products, quantities, subtotals, and total."""
    if not isinstance(cart, dict) or not cart:
        return [], Decimal("0.00")

    normalized_cart = {}

    try:
        for product_id, quantity in cart.items():
            product_id = int(product_id)
            quantity = int(quantity)

            if product_id <= 0 or quantity <= 0:
                raise CheckoutError(
                    "Your cart contains invalid quantities."
                )

            normalized_cart[product_id] = quantity

    except (TypeError, ValueError, OverflowError):
        raise CheckoutError("Your cart contains invalid items.")

    products = Product.objects.in_bulk(normalized_cart.keys())
    items = []
    total = Decimal("0.00")

    for product_id, quantity in normalized_cart.items():
        product = products.get(product_id)

        if product is None or not product.is_available:
            raise CheckoutError(
                "A product in your cart is no longer available."
            )

        if product.stock < quantity:
            raise CheckoutError(
                f"Only {product.stock} unit(s) of "
                f"{product.name} are available."
            )

        try:
            price = Decimal(str(product.price))
        except (InvalidOperation, TypeError, ValueError):
            raise CheckoutError("A product has an invalid price.")

        if not price.is_finite() or price < 0:
            raise CheckoutError("A product has an invalid price.")

        subtotal = price * quantity
        total += subtotal

        items.append(
            {
                "product": product,
                "quantity": quantity,
                "subtotal": subtotal,
            }
        )

    return items, total


def build_order_summary(order):
    """Build the progress steps displayed on the order-tracking page."""
    status = order.status

    if status == Order.Status.CANCELLED:
        return [
            {
                "label": "Order Placed",
                "description": "Your order was received.",
                "complete": True,
                "current": False,
            },
            {
                "label": "Cancelled",
                "description": "This order has been cancelled.",
                "complete": True,
                "current": True,
            },
        ]

    return [
        {
            "label": "Order Placed",
            "description": "Your order has been received.",
            "complete": True,
            "current": status == Order.Status.PLACED,
        },
        {
            "label": "Processing",
            "description": "Your order is being prepared.",
            "complete": status
            in (
                Order.Status.PROCESSING,
                Order.Status.SHIPPED,
                Order.Status.DELIVERED,
            ),
            "current": status == Order.Status.PROCESSING,
        },
        {
            "label": "Shipped",
            "description": "Your order is on its way.",
            "complete": status
            in (
                Order.Status.SHIPPED,
                Order.Status.DELIVERED,
            ),
            "current": status == Order.Status.SHIPPED,
        },
        {
            "label": "Delivered",
            "description": "Your order has been delivered.",
            "complete": status == Order.Status.DELIVERED,
            "current": status == Order.Status.DELIVERED,
        },
    ]


@login_required
def checkout(request):
    cart = request.session.get("cart", {})

    if not cart:
        messages.info(request, "Your cart is empty.")
        return redirect("cart_detail")

    try:
        items, total = get_cart_items(cart)
    except CheckoutError as exc:
        messages.error(request, str(exc))
        return redirect("cart_detail")

    if request.method == "POST":
        form = CheckoutForm(request.POST)

        if form.is_valid():
            try:
                with transaction.atomic():
                    current_cart = request.session.get("cart", {})

                    if not current_cart:
                        raise CheckoutError("Your cart is empty.")

                    validated_items, _ = get_cart_items(current_cart)

                    product_ids = sorted(
                        item["product"].pk
                        for item in validated_items
                    )

                    # Lock products on database backends that support
                    # SELECT FOR UPDATE. SQLite does not provide equivalent
                    # row-level locking guarantees.
                    locked_products = {
                        product.pk: product
                        for product in (
                            Product.objects.select_for_update()
                            .filter(pk__in=product_ids)
                            .order_by("pk")
                        )
                    }

                    order_items = []
                    total = Decimal("0.00")

                    # Recheck stock, availability, and prices using the
                    # products fetched inside the transaction.
                    for item in validated_items:
                        product = locked_products.get(
                            item["product"].pk
                        )
                        quantity = item["quantity"]

                        if product is None or not product.is_available:
                            raise CheckoutError(
                                "A product in your cart is no longer available."
                            )

                        if product.stock < quantity:
                            raise CheckoutError(
                                f"Only {product.stock} unit(s) of "
                                f"{product.name} are available."
                            )

                        try:
                            price = Decimal(str(product.price))
                        except (
                            InvalidOperation,
                            TypeError,
                            ValueError,
                        ):
                            raise CheckoutError(
                                "A product has an invalid price."
                            )

                        if not price.is_finite() or price < 0:
                            raise CheckoutError(
                                "A product has an invalid price."
                            )

                        total += price * quantity
                        order_items.append(
                            (product, quantity, price)
                        )

                    cleaned = form.cleaned_data

                    order = Order.objects.create(
                        user=request.user,
                        full_name=cleaned["full_name"],
                        email=cleaned["email"],
                        phone=cleaned["phone"],
                        address_line1=cleaned["address_line1"],
                        address_line2=cleaned.get("address_line2", ""),
                        city=cleaned["city"],
                        state=cleaned["state"],
                        postal_code=cleaned["postal_code"],
                        status=Order.Status.PLACED,
                        payment_method=Order.PaymentMethod.COD,
                        payment_status=Order.PaymentStatus.PENDING,
                        total_amount=total,
                    )

                    for product, quantity, price in order_items:
                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            product_name=product.name,
                            unit_price=price,
                            quantity=quantity,
                        )

                        product.stock -= quantity
                        product.save(update_fields=["stock"])

                    # The session cart is cleared only after all order
                    # records and stock updates have been completed.
                    request.session["cart"] = {}
                    request.session.modified = True

                messages.success(
                    request,
                    "Your order has been placed successfully.",
                )

                return redirect(
                    "order_confirmation",
                    order_id=order.pk,
                )

            except CheckoutError as exc:
                messages.error(request, str(exc))
                return redirect("checkout")

            except (InvalidOperation, TypeError, ValueError):
                messages.error(
                    request,
                    "Unable to process your order. Please check your cart.",
                )
                return redirect("checkout")

    else:
        form = CheckoutForm()

    return render(
        request,
        "orders/checkout.html",
        {
            "form": form,
            "items": items,
            "total": total,
        },
    )


@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(
        Order.objects.prefetch_related("items"),
        pk=order_id,
        user=request.user,
    )

    return render(
        request,
        "orders/order_confirmation.html",
        {"order": order},
    )


@login_required
def order_history(request):
    orders = (
        Order.objects.filter(user=request.user)
        .prefetch_related("items")
        .order_by("-created_at")
    )

    return render(
        request,
        "orders/order_history.html",
        {"orders": orders},
    )


@login_required
@require_POST
def cancel_order(request, order_id):
    with transaction.atomic():
        order = get_object_or_404(
            Order.objects.select_for_update(),
            pk=order_id,
            user=request.user,
        )

        # Only placed and processing orders can be cancelled.
        if order.status not in (
            Order.Status.PLACED,
            Order.Status.PROCESSING,
        ):
            messages.error(
                request,
                "This order can no longer be cancelled.",
            )
            return redirect("order_history")

        items = list(order.items.all())

        product_ids = sorted(
            {
                item.product_id
                for item in items
                if item.product_id is not None
            }
        )

        locked_products = {
            product.pk: product
            for product in (
                Product.objects.select_for_update()
                .filter(pk__in=product_ids)
                .order_by("pk")
            )
        }

        # Restore stock before changing the order status. Both operations
        # occur in the same transaction.
        for item in items:
            product = locked_products.get(item.product_id)

            if product is not None:
                product.stock += item.quantity
                product.save(update_fields=["stock"])

        order.status = Order.Status.CANCELLED
        order.save(update_fields=["status", "updated_at"])

    messages.success(
        request,
        f"Order #{order.pk} has been cancelled successfully.",
    )

    return redirect("order_history")


@login_required
def order_tracking(request, order_id):
    order = get_object_or_404(
        Order.objects.prefetch_related("items"),
        pk=order_id,
        user=request.user,
    )

    return render(
        request,
        "orders/order_tracking.html",
        {
            "order": order,
            "tracking_steps": build_order_summary(order),
        },
    )
