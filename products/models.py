
"""
Database model for Shopora products.
"""

from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(
        unique=True,
        blank=True,
    )
    description = models.TextField()
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(
        upload_to="products/",
        blank=True,
        null=True,
    )
    is_available = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        """Generate a unique slug when one has not been provided."""
        if not self.slug:
            base_slug = slugify(self.name) or "product"
            slug = base_slug
            counter = 1

            while Product.objects.filter(
                slug=slug,
            ).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """Return the canonical URL for this product."""
        return reverse(
            "product_detail",
            kwargs={"slug": self.slug},
        )

    def __str__(self):
        return self.name
