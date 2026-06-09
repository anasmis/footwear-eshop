from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Category, Product, Review


class ProductModelTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Ordinateurs")
        self.product = Product.objects.create(
            name="PC Portable Test",
            description="Un bon PC",
            price=Decimal("5000.00"),
            stock=5,
            category=self.category,
        )

    def test_slug_is_generated(self):
        self.assertTrue(self.product.slug)

    def test_category_slug_is_generated(self):
        self.assertEqual(self.category.slug, "ordinateurs")

    def test_in_stock_property(self):
        self.assertTrue(self.product.in_stock)
        self.product.stock = 0
        self.assertFalse(self.product.in_stock)

    def test_average_rating(self):
        user = User.objects.create_user("client1", password="pass12345")
        Review.objects.create(product=self.product, user=user, rating=4)
        self.assertEqual(self.product.average_rating, 4)
        self.assertEqual(self.product.review_count, 1)


class ProductViewTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Téléphones")
        self.product = Product.objects.create(
            name="Smartphone Test",
            description="Téléphone",
            price=Decimal("3000.00"),
            stock=10,
            category=self.category,
        )

    def test_product_list_status(self):
        response = self.client.get(reverse("products:product_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Smartphone Test")

    def test_product_detail_status(self):
        response = self.client.get(self.product.get_absolute_url())
        self.assertEqual(response.status_code, 200)

    def test_search_filters_results(self):
        response = self.client.get(reverse("products:product_list"), {"q": "Smartphone"})
        self.assertContains(response, "Smartphone Test")

    def test_home_page_status(self):
        response = self.client.get(reverse("products:home"))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_requires_staff(self):
        response = self.client.get(reverse("dashboard:home"))
        self.assertEqual(response.status_code, 302)  # redirige vers login


class RecommendationTests(TestCase):
    def setUp(self):
        from recommendation.engine import reset_cache

        reset_cache()
        laptops = Category.objects.create(name="Ordinateurs portables")
        phones = Category.objects.create(name="Téléphones")
        self.laptop1 = Product.objects.create(
            name="PC Portable UltraBook",
            description="Ordinateur portable léger avec SSD et processeur rapide",
            price=Decimal("8000.00"), stock=5, category=laptops,
        )
        self.laptop2 = Product.objects.create(
            name="PC Portable Gamer",
            description="Ordinateur portable puissant pour le jeu avec carte graphique",
            price=Decimal("15000.00"), stock=5, category=laptops,
        )
        self.phone = Product.objects.create(
            name="Smartphone Galaxy",
            description="Téléphone mobile avec grand écran et bon appareil photo",
            price=Decimal("4000.00"), stock=5, category=phones,
        )

    def test_recommends_same_category_first(self):
        from recommendation.engine import get_recommendations

        recs = get_recommendations(self.laptop1, k=2)
        self.assertIn(self.laptop2, recs)
        self.assertNotIn(self.laptop1, recs)  # n'inclut pas le produit lui-même

    def test_recommendations_appear_on_detail_page(self):
        response = self.client.get(self.laptop1.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Vous aimerez aussi")
