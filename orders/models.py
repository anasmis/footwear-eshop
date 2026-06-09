from decimal import Decimal

from django.contrib.auth.models import User
from django.db import models

from products.models import Product


class Order(models.Model):
    """Commande validée par un client."""

    STATUS_PENDING = "pending"
    STATUS_CONFIRMED = "confirmed"
    STATUS_PREPARING = "preparing"
    STATUS_SHIPPED = "shipped"
    STATUS_DELIVERED = "delivered"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (STATUS_PENDING, "En attente"),
        (STATUS_CONFIRMED, "Confirmée"),
        (STATUS_PREPARING, "En préparation"),
        (STATUS_SHIPPED, "Expédiée"),
        (STATUS_DELIVERED, "Livrée"),
        (STATUS_CANCELLED, "Annulée"),
    ]

    user = models.ForeignKey(
        User, verbose_name="Client", on_delete=models.CASCADE, related_name="orders"
    )
    full_name = models.CharField("Nom complet", max_length=150)
    address = models.CharField("Adresse", max_length=255)
    city = models.CharField("Ville", max_length=100)
    postal_code = models.CharField("Code postal", max_length=20)
    phone = models.CharField("Téléphone", max_length=30)
    status = models.CharField(
        "Statut", max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING
    )
    created_at = models.DateTimeField("Date de commande", auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Commande"
        verbose_name_plural = "Commandes"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Commande #{self.pk} - {self.user.username}"

    @property
    def total(self):
        return sum((line.subtotal for line in self.items.all()), Decimal("0.00"))

    @property
    def total_items(self):
        return sum(line.quantity for line in self.items.all())


class OrderItem(models.Model):
    """Ligne de commande : un produit avec sa quantité et son prix unitaire."""

    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="items"
    )
    product = models.ForeignKey(
        Product,
        verbose_name="Produit",
        on_delete=models.SET_NULL,
        null=True,
        related_name="order_items",
    )
    product_name = models.CharField("Nom du produit", max_length=200)
    price = models.DecimalField("Prix unitaire", max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField("Quantité", default=1)

    class Meta:
        verbose_name = "Ligne de commande"
        verbose_name_plural = "Lignes de commande"

    def __str__(self):
        return f"{self.quantity} x {self.product_name}"

    @property
    def subtotal(self):
        return self.price * self.quantity
