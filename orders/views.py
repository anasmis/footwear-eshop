from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from cart.models import Cart

from .forms import CheckoutForm
from .models import Order, OrderItem


@login_required
def checkout(request):
    cart = Cart.objects.filter(user=request.user).first()
    items = cart.items.select_related("product").all() if cart else []

    if not items:
        messages.warning(request, "Votre panier est vide.")
        return redirect("products:product_list")

    # Pré-remplit avec le profil du client si disponible.
    profile = getattr(request.user, "profile", None)
    initial = {
        "full_name": request.user.get_full_name() or request.user.username,
        "address": getattr(profile, "address", ""),
        "city": getattr(profile, "city", ""),
        "postal_code": getattr(profile, "postal_code", ""),
        "phone": getattr(profile, "phone", ""),
    }

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                # Vérifie le stock avant de valider.
                for item in items:
                    if item.quantity > item.product.stock:
                        messages.error(
                            request,
                            f"Stock insuffisant pour « {item.product.name} ».",
                        )
                        return redirect("cart:cart_detail")

                order = form.save(commit=False)
                order.user = request.user
                order.save()

                for item in items:
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        product_name=item.product.name,
                        price=item.product.price,
                        quantity=item.quantity,
                    )
                    # Décrémente le stock.
                    item.product.stock -= item.quantity
                    item.product.save(update_fields=["stock"])

                cart.items.all().delete()

            messages.success(
                request, f"Votre commande #{order.pk} a été enregistrée avec succès."
            )
            return redirect("orders:order_detail", pk=order.pk)
    else:
        form = CheckoutForm(initial=initial)

    return render(
        request,
        "orders/checkout.html",
        {"form": form, "cart": cart, "items": items},
    )


@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).prefetch_related("items")
    return render(request, "orders/order_list.html", {"orders": orders})


@login_required
def order_detail(request, pk):
    order = get_object_or_404(
        Order.objects.prefetch_related("items"), pk=pk, user=request.user
    )
    return render(request, "orders/order_detail.html", {"order": order})
