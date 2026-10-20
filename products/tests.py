
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from .models import Product


class ProductModelTests(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="Wireless Mouse",
            description="A wireless mouse for everyday use.",
            price=Decimal("799.00"),
            stock=10,
            is_available=True,
        )

    def test_product_string_representation(self):
        self.assertEqual(str(self.product), "Wireless Mouse")

    def test_product_slug_is_generated(self):
        self.assertEqual(self.product.slug, "wireless-mouse")

    def test_product_detail_url(self):
        self.assertEqual(
            self.product.get_absolute_url(),
            reverse(
                "product_detail",
                kwargs={"slug": self.product.slug},
            ),
        )


class ProductViewTests(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="Wireless Mouse",
            description="A wireless mouse for everyday use.",
            price=Decimal("799.00"),
            stock=10,
            is_available=True,
        )

    def test_product_catalogue_loads(self):
        response = self.client.get(reverse("product_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Wireless Mouse")
