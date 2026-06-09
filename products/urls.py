from django.urls import path

from . import views

app_name = "products"

urlpatterns = [
    path("", views.home, name="home"),
    path("produits/", views.product_list, name="product_list"),
    path("product/<slug:slug>/", views.product_detail, name="product_detail"),
    path("product/<slug:slug>/review/", views.add_review, name="add_review"),
]
