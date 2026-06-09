from django.contrib.auth.models import User
from django.db import models
from django.db.models import Avg
from django.urls import reverse
from django.utils.text import slugify


class Category(models.Model):
    """Catégorie de produits (ex: Ordinateurs, Téléphones, Accessoires)."""

    name = models.CharField("Nom", max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField("Description", blank=True)
    created_at = models.DateTimeField("Date d'ajout", auto_now_add=True)

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("products:product_list") + f"?category={self.slug}"


class Product(models.Model):
    """Produit vendu sur la plateforme."""

    GENDER_CHOICES = [
        ("Men", "Homme"),
        ("Women", "Femme"),
        ("Boys", "Garçon"),
        ("Girls", "Fille"),
    ]

    name = models.CharField("Nom", max_length=200)
    gender = models.CharField(
        "Genre", max_length=10, choices=GENDER_CHOICES, blank=True
    )
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField("Description")
    price = models.DecimalField("Prix", max_digits=10, decimal_places=2)
    image = models.ImageField("Image", upload_to="products/", blank=True, null=True)
    image_url = models.URLField("Image (URL externe)", max_length=500, blank=True)
    category = models.ForeignKey(
        Category,
        verbose_name="Catégorie",
        on_delete=models.CASCADE,
        related_name="products",
    )
    stock = models.PositiveIntegerField("Quantité en stock", default=0)
    available = models.BooleanField("Disponible", default=True)
    created_at = models.DateTimeField("Date d'ajout", auto_now_add=True)
    updated_at = models.DateTimeField("Dernière modification", auto_now=True)

    class Meta:
        verbose_name = "Produit"
        verbose_name_plural = "Produits"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)
            slug = base
            counter = 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("products:product_detail", args=[self.slug])

    @property
    def display_image(self):
        """URL de l'image : fichier uploadé en priorité, sinon URL externe."""
        if self.image:
            return self.image.url
        return self.image_url or ""

    @property
    def in_stock(self):
        return self.available and self.stock > 0

    @property
    def average_rating(self):
        result = self.reviews.aggregate(avg=Avg("rating"))
        return round(result["avg"], 1) if result["avg"] else 0

    @property
    def review_count(self):
        return self.reviews.count()


class Review(models.Model):
    """Avis (note + commentaire) laissé par un client sur un produit."""

    RATING_CHOICES = [(i, f"{i} étoile{'s' if i > 1 else ''}") for i in range(1, 6)]

    product = models.ForeignKey(
        Product,
        verbose_name="Produit",
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    user = models.ForeignKey(
        User, verbose_name="Client", on_delete=models.CASCADE, related_name="reviews"
    )
    rating = models.PositiveSmallIntegerField("Note", choices=RATING_CHOICES, default=5)
    comment = models.TextField("Commentaire", blank=True)
    created_at = models.DateTimeField("Date", auto_now_add=True)

    class Meta:
        verbose_name = "Avis"
        verbose_name_plural = "Avis"
        ordering = ["-created_at"]
        # Un client ne peut laisser qu'un seul avis par produit.
        unique_together = ("product", "user")

    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.rating}/5)"
