from .models import Cart


def cart_summary(request):
    """Expose le nombre d'articles du panier à tous les templates."""
    count = 0
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            count = cart.total_items
    return {"cart_count": count}
