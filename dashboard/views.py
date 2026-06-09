from decimal import Decimal

from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.db.models import Count, DecimalField, F, Sum
from django.db.models.functions import Coalesce
from django.shortcuts import render

from orders.models import Order, OrderItem
from products.models import Product


def is_staff(user):
    return user.is_active and user.is_staff


@user_passes_test(is_staff, login_url="accounts:login")
def dashboard_home(request):
    # Chiffre d'affaires : on exclut les commandes annulées.
    paid_orders = Order.objects.exclude(status=Order.STATUS_CANCELLED)

    revenue = (
        OrderItem.objects.filter(order__in=paid_orders).aggregate(
            total=Coalesce(
                Sum(
                    F("price") * F("quantity"),
                    output_field=DecimalField(max_digits=12, decimal_places=2),
                ),
                Decimal("0.00"),
            )
        )["total"]
    )

    # Produits les plus vendus.
    best_sellers = (
        OrderItem.objects.filter(order__in=paid_orders)
        .values("product_name")
        .annotate(sold=Sum("quantity"))
        .order_by("-sold")[:5]
    )

    # Répartition des commandes par statut.
    status_counts = {
        label: Order.objects.filter(status=key).count()
        for key, label in Order.STATUS_CHOICES
    }

    context = {
        "total_products": Product.objects.count(),
        "total_clients": User.objects.filter(is_staff=False).count(),
        "total_orders": Order.objects.count(),
        "revenue": revenue,
        "best_sellers": best_sellers,
        "recent_orders": Order.objects.select_related("user").order_by("-created_at")[:8],
        "status_counts": status_counts,
        "low_stock": Product.objects.filter(stock__lte=5).order_by("stock")[:5],
    }
    return render(request, "dashboard/home.html", context)
