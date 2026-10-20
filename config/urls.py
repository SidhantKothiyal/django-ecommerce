
"""
URL configuration for the ecommerce project.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    # Django administration
    path("admin/", admin.site.urls),

    # Customer accounts
    path("accounts/", include("accounts.urls")),

    # Shopping cart and orders
    path("orders/", include("orders.urls")),

    # Product catalogue and homepage
    path("", include("products.urls")),
]


# Serve uploaded media files during local development only.
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
