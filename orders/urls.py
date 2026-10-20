"""
URL routes for Shopora checkout, orders, and order tracking.
"""

from django.urls import path

from . import views


urlpatterns = [
    path("checkout/", views.checkout, name="checkout"),
    path(
        "confirmation/<int:order_id>/",
        views.order_confirmation,
        name="order_confirmation",
    ),
    path("history/", views.order_history, name="order_history"),
    path(
        "<int:order_id>/tracking/",
        views.order_tracking,
        name="order_tracking",
    ),
    path(
        "<int:order_id>/cancel/",
        views.cancel_order,
        name="cancel_order",
    ),
]