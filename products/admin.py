from django.contrib import admin

from .models import Category, Product, Review


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_at")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "gender", "price", "stock", "available", "created_at")
    list_filter = ("available", "category", "gender", "created_at")
    list_editable = ("price", "stock", "available")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    date_hierarchy = "created_at"


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("product", "user", "rating", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("product__name", "user__username", "comment")
