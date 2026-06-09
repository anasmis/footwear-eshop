"""Commande de peuplement : crée des catégories et produits de démonstration.

Usage : python manage.py seed_data
"""

from decimal import Decimal

from django.core.management.base import BaseCommand

from products.models import Category, Product

CATEGORIES = {
    "Ordinateurs portables": [
        ("PC Portable UltraBook 14", "Ultrabook léger 14 pouces, Intel Core i5, 16 Go RAM, SSD 512 Go.", "8990.00", 12),
        ("PC Portable Gamer 15", "Ordinateur gamer 15.6 pouces, RTX 4060, Core i7, 32 Go RAM.", "15990.00", 6),
        ("PC Portable Pro 13", "Station de travail compacte, écran 13 pouces, autonomie 12h.", "10490.00", 9),
    ],
    "Téléphones": [
        ("Smartphone Galaxy X", "Smartphone 6.5 pouces AMOLED, 128 Go, triple capteur photo.", "4290.00", 20),
        ("Smartphone Pixel Lite", "Téléphone Android pur, excellent appareil photo, 5G.", "3590.00", 15),
        ("Smartphone Eco 5G", "Modèle abordable 5G, grande batterie 5000 mAh.", "1990.00", 25),
    ],
    "Accessoires": [
        ("Souris sans fil ergonomique", "Souris Bluetooth silencieuse, batterie longue durée.", "199.00", 50),
        ("Clavier mécanique RGB", "Clavier mécanique rétroéclairé, switchs rouges.", "549.00", 30),
        ("Sac à dos pour PC 15.6", "Sac à dos résistant à l'eau avec compartiment ordinateur.", "299.00", 40),
        ("Casque audio sans fil", "Casque circum-aural à réduction de bruit active.", "899.00", 18),
    ],
    "Écrans": [
        ("Écran 24 pouces Full HD", "Moniteur IPS 24 pouces 75 Hz, bordures fines.", "1290.00", 14),
        ("Écran 27 pouces 2K", "Moniteur 27 pouces QHD 144 Hz pour le gaming.", "2790.00", 8),
    ],
    "Stockage": [
        ("Disque SSD externe 1 To", "SSD portable USB-C, vitesses jusqu'à 1050 Mo/s.", "899.00", 35),
        ("Clé USB 128 Go", "Clé USB 3.2 rapide et compacte.", "149.00", 60),
    ],
}


class Command(BaseCommand):
    help = "Peuple la base avec des catégories et produits de démonstration."

    def handle(self, *args, **options):
        created_products = 0
        for cat_name, products in CATEGORIES.items():
            category, _ = Category.objects.get_or_create(name=cat_name)
            for name, desc, price, stock in products:
                _, created = Product.objects.get_or_create(
                    name=name,
                    defaults={
                        "description": desc,
                        "price": Decimal(price),
                        "stock": stock,
                        "category": category,
                        "available": True,
                    },
                )
                if created:
                    created_products += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Données créées : {Category.objects.count()} catégories, "
                f"{created_products} nouveaux produits."
            )
        )
