from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from products.models import Product
from .models import Order, OrderItem


class OrderManagementTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="customer",
            email="customer@example.com",
            password="StrongTestPassword123!",
        )

        self.product = Product.objects.create(
            name="Wireless Mouse",
            description="Wireless mouse",
            price=Decimal("799.00"),
            stock=10,
            is_available=True,
        )

        self.checkout_data = {
            "full_name": "Test Customer",
            "email": "customer@example.com",
            "phone": "9876543210",
            "address_line1": "House 12, Main Road",
            "address_line2": "",
            "city": "Rohtak",
            "state": "Haryana",
            "postal_code": "124001",
        }

    def add_product_to_cart(self, quantity=2):
        session = self.client.session
        session["cart"] = {
            str(self.product.pk): quantity,
        }
        session.save()

    def create_order(self, status=Order.Status.PLACED):
        """Create an order representing two already-purchased units."""
        self.product.stock = 8
        self.product.save(update_fields=["stock"])

        order = Order.objects.create(
            user=self.user,
            full_name="Test Customer",
            email="customer@example.com",
            phone="9876543210",
            address_line1="House 12, Main Road",
            address_line2="",
            city="Rohtak",
            state="Haryana",
            postal_code="124001",
            status=status,
            payment_method=Order.PaymentMethod.COD,
            payment_status=Order.PaymentStatus.PENDING,
            total_amount=Decimal("1598.00"),
        )

        OrderItem.objects.create(
            order=order,
            product=self.product,
            product_name=self.product.name,
            unit_price=Decimal("799.00"),
            quantity=2,
        )

        return order

    def test_checkout_requires_login(self):
        response = self.client.get(reverse("checkout"))

        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_empty_cart_redirects_to_cart(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("checkout"))

        self.assertRedirects(
            response,
            reverse("cart_detail"),
        )
        self.assertEqual(Order.objects.count(), 0)

    def test_checkout_page_loads(self):
        self.client.force_login(self.user)
        self.add_product_to_cart()

        response = self.client.get(reverse("checkout"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Delivery Details")
        self.assertContains(response, "Wireless Mouse")
        self.assertContains(response, "1598.00")

    def test_successful_checkout_creates_order(self):
        self.client.force_login(self.user)
        self.add_product_to_cart(quantity=2)

        response = self.client.post(
            reverse("checkout"),
            self.checkout_data,
        )

        self.assertEqual(Order.objects.count(), 1)
        order = Order.objects.get()

        self.assertEqual(order.user, self.user)
        self.assertEqual(
            order.total_amount,
            Decimal("1598.00"),
        )
        self.assertEqual(order.status, Order.Status.PLACED)
        self.assertEqual(
            order.payment_method,
            Order.PaymentMethod.COD,
        )
        self.assertEqual(order.items.count(), 1)

        item = order.items.get()

        self.assertEqual(item.product_name, "Wireless Mouse")
        self.assertEqual(item.quantity, 2)
        self.assertEqual(
            item.unit_price,
            Decimal("799.00"),
        )
        self.assertEqual(
            item.subtotal,
            Decimal("1598.00"),
        )

        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 8)

        self.assertRedirects(
            response,
            reverse("order_confirmation", args=[order.pk]),
        )
        self.assertEqual(
            self.client.session.get("cart", {}),
            {},
        )

    def test_invalid_checkout_does_not_create_order(self):
        self.client.force_login(self.user)
        self.add_product_to_cart()

        invalid_data = self.checkout_data.copy()
        invalid_data["email"] = "not-an-email"

        response = self.client.post(
            reverse("checkout"),
            invalid_data,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Order.objects.count(), 0)

        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 10)
        self.assertEqual(
            self.client.session["cart"],
            {str(self.product.pk): 2},
        )

    def test_quantity_above_stock_does_not_create_order(self):
        self.client.force_login(self.user)
        self.add_product_to_cart(quantity=11)

        response = self.client.post(
            reverse("checkout"),
            self.checkout_data,
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Order.objects.count(), 0)

        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 10)

    def test_customer_cannot_view_another_users_order(self):
        order = Order.objects.create(
            user=self.user,
            full_name="Test Customer",
            email="customer@example.com",
            phone="9876543210",
            address_line1="House 12, Main Road",
            city="Rohtak",
            state="Haryana",
            postal_code="124001",
            total_amount=Decimal("799.00"),
        )

        another_user = User.objects.create_user(
            username="another_customer",
            password="AnotherStrongPassword123!",
        )
        self.client.force_login(another_user)

        response = self.client.get(
            reverse("order_confirmation", args=[order.pk])
        )

        self.assertEqual(response.status_code, 404)

    def test_order_history_only_shows_logged_in_users_orders(self):
        Order.objects.create(
            user=self.user,
            full_name="Test Customer",
            email="customer@example.com",
            phone="9876543210",
            address_line1="House 12, Main Road",
            city="Rohtak",
            state="Haryana",
            postal_code="124001",
            total_amount=Decimal("799.00"),
        )

        self.client.force_login(self.user)

        response = self.client.get(reverse("order_history"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["orders"]), 1)

    # Phase 3: Order cancellation tests

    def test_cancel_order_restores_stock(self):
        order = self.create_order()
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("cancel_order", args=[order.pk])
        )

        order.refresh_from_db()
        self.product.refresh_from_db()

        self.assertRedirects(
            response,
            reverse("order_history"),
        )
        self.assertEqual(order.status, Order.Status.CANCELLED)
        self.assertEqual(self.product.stock, 10)

    def test_repeated_cancellation_does_not_restore_stock_twice(self):
        order = self.create_order()
        self.client.force_login(self.user)

        self.client.post(
            reverse("cancel_order", args=[order.pk])
        )

        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 10)

        self.client.post(
            reverse("cancel_order", args=[order.pk])
        )

        order.refresh_from_db()
        self.product.refresh_from_db()

        self.assertEqual(order.status, Order.Status.CANCELLED)
        self.assertEqual(self.product.stock, 10)

    def test_get_request_cannot_cancel_order(self):
        order = self.create_order()
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("cancel_order", args=[order.pk])
        )

        order.refresh_from_db()
        self.product.refresh_from_db()

        self.assertEqual(response.status_code, 405)
        self.assertEqual(order.status, Order.Status.PLACED)
        self.assertEqual(self.product.stock, 8)

    def test_customer_cannot_cancel_another_users_order(self):
        order = self.create_order()

        another_user = User.objects.create_user(
            username="another_customer",
            password="AnotherStrongPassword123!",
        )
        self.client.force_login(another_user)

        response = self.client.post(
            reverse("cancel_order", args=[order.pk])
        )

        order.refresh_from_db()
        self.product.refresh_from_db()

        self.assertEqual(response.status_code, 404)
        self.assertEqual(order.status, Order.Status.PLACED)
        self.assertEqual(self.product.stock, 8)
