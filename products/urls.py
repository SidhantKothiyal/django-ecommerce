
"""
URL routes for Shopora products and shopping cart.
"""

from django.urls import path

from . import views


urlpatterns = [
    # Product catalogue and homepage
    path(
        "",
        views.product_list,
        name="product_list",
    ),

    # Product detail using a unique slug
    path(
        "products/<slug:slug>/",
        views.product_detail,
        name="product_detail",
    ),

    # Shopping cart
    path(
        "cart/",
        views.cart_detail,
        name="cart_detail",
    ),

    # Add a product to the cart
    path(
        "cart/add/<int:product_id>/",
        views.cart_add,
        name="cart_add",
    ),

    # Update cart quantity
    path(
        "cart/update/<int:product_id>/",
        views.cart_update,
        name="cart_update",
    ),

    # Remove a product from the cart
    path(
        "cart/remove/<int:product_id>/",
        views.cart_remove,
        name="cart_remove",
    ),
]
