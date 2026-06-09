from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from products.models import Product

from .models import Cart, CartItem


def _get_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart


@login_required
def cart_detail(request):
    cart = _get_cart(request.user)
    items = cart.items.select_related("product").all()
    return render(request, "cart/cart_detail.html", {"cart": cart, "items": items})


@login_required
@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id, available=True)
    if not product.in_stock:
        messages.error(request, "Ce produit n'est plus en stock.")
        return redirect(product.get_absolute_url())

    quantity = int(request.POST.get("quantity", 1) or 1)
    quantity = max(1, min(quantity, product.stock))

    cart = _get_cart(request.user)
    item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        item.quantity = min(item.quantity + quantity, product.stock)
    else:
        item.quantity = quantity
    item.save()

    messages.success(request, f"« {product.name} » a été ajouté au panier.")
    return redirect("cart:cart_detail")


@login_required
@require_POST
def update_cart(request, item_id):
    item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
    quantity = int(request.POST.get("quantity", 1) or 1)
    if quantity < 1:
        item.delete()
        messages.info(request, "Produit retiré du panier.")
    else:
        item.quantity = min(quantity, item.product.stock)
        item.save()
        messages.success(request, "Panier mis à jour.")
    return redirect("cart:cart_detail")


@login_required
@require_POST
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
    item.delete()
    messages.info(request, "Produit retiré du panier.")
    return redirect("cart:cart_detail")


@login_required
@require_POST
def clear_cart(request):
    cart = _get_cart(request.user)
    cart.items.all().delete()
    messages.info(request, "Le panier a été vidé.")
    return redirect("cart:cart_detail")
