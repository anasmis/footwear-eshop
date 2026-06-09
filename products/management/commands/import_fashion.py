"""Importe le dataset fashion.csv (boutique de CHAUSSURES) dans la base.

- On ne conserve que les lignes ``SubCategory == 'Shoes'``.
- La catégorie du shop = colonne **ProductType** (Casual Shoes, Sports Shoes,
  Heels, Flats, Formal Shoes).
- Le **genre** (Men/Women) est stocké pour pouvoir séparer Homme / Femme.
- On importe au maximum N produits par catégorie (50 par défaut).
- Le prix (absent du dataset) est généré aléatoirement par catégorie,
  de façon déterministe (seed = ProductId) pour rester stable.
- La description est synthétisée à partir de Gender / Usage / Colour / ProductType
  (elle alimente aussi le moteur de recommandation TF-IDF).
- L'image est référencée via son URL externe (ImageURL).

Usage : python manage.py import_fashion [--per-category 50] [--csv fashion.csv]
"""

import csv
import random
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from products.models import Category, Product

# On ne garde que cette sous-catégorie (boutique de chaussures).
ALLOWED_SUBCATEGORY = "Shoes"

# Fourchettes de prix (MAD) par ProductType : (min, max).
PRICE_RANGES = {
    "Casual Shoes": (250, 1000),
    "Sports Shoes": (350, 1500),
    "Heels": (300, 1200),
    "Flats": (200, 800),
    "Formal Shoes": (400, 1600),
}
DEFAULT_RANGE = (250, 1200)


class Command(BaseCommand):
    help = "Importe fashion.csv (chaussures uniquement, 50 produits par type)."

    def add_arguments(self, parser):
        parser.add_argument("--per-category", type=int, default=50)
        parser.add_argument("--csv", type=str, default="fashion.csv")
        parser.add_argument(
            "--keep",
            action="store_true",
            help="Conserve les produits existants (par défaut on les supprime).",
        )

    def handle(self, *args, **options):
        csv_path = Path(options["csv"])
        if not csv_path.is_absolute():
            csv_path = settings.BASE_DIR / csv_path
        if not csv_path.exists():
            raise CommandError(f"Fichier introuvable : {csv_path}")

        per_category = options["per_category"]

        with open(csv_path, encoding="utf-8") as f:
            rows = [
                r
                for r in csv.DictReader(f)
                if (r.get("SubCategory") or "").strip() == ALLOWED_SUBCATEGORY
            ]

        if not options["keep"]:
            Product.objects.all().delete()
            Category.objects.all().delete()
            self.stdout.write("Anciens produits/catégories supprimés.")

        # Regroupe les chaussures par ProductType (= catégorie du shop).
        by_category = {}
        for row in rows:
            ptype = (row.get("ProductType") or "").strip()
            if ptype:
                by_category.setdefault(ptype, []).append(row)

        total = 0
        for type_name, items in by_category.items():
            category, _ = Category.objects.get_or_create(
                name=type_name,
                defaults={"description": f"Chaussures de type {type_name}."},
            )
            low, high = PRICE_RANGES.get(type_name, DEFAULT_RANGE)

            created_in_cat = 0
            for row in items:
                if created_in_cat >= per_category:
                    break

                title = (row.get("ProductTitle") or "").strip()
                if not title:
                    continue

                # Prix déterministe basé sur le ProductId.
                try:
                    seed = int(row.get("ProductId") or 0)
                except ValueError:
                    seed = abs(hash(title)) % 100000
                rng = random.Random(seed)
                price = Decimal(rng.randint(low, high))
                stock = rng.randint(0, 40)

                Product.objects.create(
                    name=title,
                    gender=(row.get("Gender") or "").strip(),
                    description=self._build_description(row),
                    price=price,
                    image_url=(row.get("ImageURL") or "").strip(),
                    category=category,
                    stock=stock,
                    available=True,
                )
                created_in_cat += 1
                total += 1

            self.stdout.write(f"  {type_name}: {created_in_cat} produits")

        self.stdout.write(
            self.style.SUCCESS(
                f"Import terminé : {Category.objects.count()} catégories, "
                f"{total} produits (chaussures)."
            )
        )

    @staticmethod
    def _build_description(row):
        gender = (row.get("Gender") or "").strip()
        usage = (row.get("Usage") or "").strip()
        colour = (row.get("Colour") or "").strip()
        ptype = (row.get("ProductType") or "").strip()
        title = (row.get("ProductTitle") or "").strip()

        parts = []
        if ptype:
            article = f"{ptype}"
            if gender:
                article += f" pour {gender}"
            parts.append(article + ".")
        if colour:
            parts.append(f"Couleur : {colour}.")
        if usage:
            parts.append(f"Style : {usage}.")
        parts.append(title + ".")
        return " ".join(parts)
