
from decimal import Decimal, InvalidOperation

from .models import Product


CART_SESSION_ID = "cart"


def get_cart(request):
    """Return the cart stored in the session."""
    cart = request.session.get(CART_SESSION_ID, {})
    return cart if isinstance(cart, dict) else {}


def save_cart(request, cart):
    """Save cart changes to the session."""
    request.session[CART_SESSION_ID] = cart
    request.session.modified = True


def _get_quantity(value):
    """Convert a valid positive whole-number quantity to int."""
    if isinstance(value, bool):
        raise ValueError("Invalid quantity.")

    try:
        quantity = int(value)
    except (TypeError, ValueError, OverflowError):
        raise ValueError("Invalid quantity.")

    if str(value).strip() != str(quantity) or quantity < 1:
        raise ValueError("Quantity must be a positive whole number.")

    return quantity


def add_to_cart(request, product, quantity=1):
    """Add a product or increase its quantity in the cart."""
    if not product.is_available:
        raise ValueError("This product is currently unavailable.")

    quantity = _get_quantity(quantity)
    cart = get_cart(request)
    product_id = str(product.pk)

    try:
        current_quantity = _get_quantity(cart.get(product_id, 0))
    except ValueError:
        current_quantity = 0

    new_quantity = current_quantity + quantity

    if new_quantity > product.stock:
        raise ValueError("Requested quantity exceeds available stock.")

    cart[product_id] = new_quantity
    save_cart(request, cart)


def update_cart(request, product, quantity):
    """Set a product's quantity in the cart."""
    if not product.is_available:
        raise ValueError("This product is currently unavailable.")

    quantity = _get_quantity(quantity)

    if quantity > product.stock:
        raise ValueError("Requested quantity exceeds available stock.")

    cart = get_cart(request)
    product_id = str(product.pk)

    if product_id in cart:
        cart[product_id] = quantity
        save_cart(request, cart)


def remove_from_cart(request, product):
    """Remove a product from the cart."""
    cart = get_cart(request)
    cart.pop(str(product.pk), None)
    save_cart(request, cart)


def get_cart_items(request):
    """Return available cart products with quantities and subtotals."""
    cart = get_cart(request)
    items = []
    valid_cart = {}

    for raw_product_id, raw_quantity in cart.items():
        try:
            product_id = int(raw_product_id)
            quantity = _get_quantity(raw_quantity)
        except (TypeError, ValueError, OverflowError):
            continue

        if product_id <= 0:
            continue

        product = Product.objects.filter(
            pk=product_id,
            is_available=True,
        ).first()

        if product is None:
            continue

        # Keep the cart quantity even if stock later changes.
        # Checkout must revalidate stock before placing the order.
        valid_cart[str(product.pk)] = quantity

        try:
            price = Decimal(str(product.price))
        except (InvalidOperation, TypeError, ValueError):
            continue

        if not price.is_finite() or price < 0:
            continue

        items.append(
            {
                "product": product,
                "quantity": quantity,
                "subtotal": price * quantity,
            }
        )

    if valid_cart != cart:
        save_cart(request, valid_cart)

    return items


def get_cart_total(request):
    """Calculate the total value of the cart."""
    return sum(
        (item["subtotal"] for item in get_cart_items(request)),
        Decimal("0.00"),
    )
