"""URL configuration for ecommerce_project."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("cart/", include("cart.urls")),
    path("orders/", include("orders.urls")),
    path("dashboard/", include("dashboard.urls")),
    path("", include("products.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = "E-Shop Django - Administration"
admin.site.site_title = "E-Shop Django"
admin.site.index_title = "Gestion de la plateforme"
