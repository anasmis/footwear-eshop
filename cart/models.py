from decimal import Decimal

from django.contrib.auth.models import User
from django.db import models

from products.models import Product


class Cart(models.Model):
    """Panier d'un client (un panier persistant par utilisateur)."""

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="cart"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Panier"
        verbose_name_plural = "Paniers"

    def __str__(self):
        return f"Panier de {self.user.username}"

    @property
    def total(self):
        return sum((item.subtotal for item in self.items.all()), Decimal("0.00"))

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    """Ligne de panier : un produit ajouté avec une quantité."""

    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="cart_items"
    )
    quantity = models.PositiveIntegerField("Quantité", default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Ligne de panier"
        verbose_name_plural = "Lignes de panier"
        unique_together = ("cart", "product")

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    @property
    def subtotal(self):
        return self.product.price * self.quantity
