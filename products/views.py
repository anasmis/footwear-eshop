from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from recommendation.engine import get_recommendations

from .forms import ReviewForm
from .models import Category, Product


# Libellés français + icône pour chaque type de chaussure (ProductType).
SHOE_LABELS = {
    "Casual Shoes": ("Chaussures décontractées", "bi-bag"),
    "Sports Shoes": ("Chaussures de sport", "bi-lightning-charge"),
    "Heels": ("Talons", "bi-gem"),
    "Flats": ("Ballerines", "bi-flower1"),
    "Formal Shoes": ("Chaussures de ville", "bi-briefcase"),
}


def home(request):
    """Page d'accueil : hero, catégories, et chaussures Homme / Femme."""
    available = Product.objects.filter(available=True).select_related("category")

    categories = list(Category.objects.annotate(n=Count("products")).order_by("-n")[:6])
    for category in categories:
        label, icon = SHOE_LABELS.get(category.name, (category.name, "bi-bag"))
        category.label = label
        category.icon = icon

    context = {
        "categories": categories,
        "men_products": available.filter(gender="Men").order_by("-created_at")[:8],
        "women_products": available.filter(gender="Women").order_by("-created_at")[:8],
        "total_products": available.count(),
        "total_categories": Category.objects.count(),
        "men_count": available.filter(gender="Men").count(),
        "women_count": available.filter(gender="Women").count(),
    }
    return render(request, "products/home.html", context)


def product_list(request):
    """Catalogue : recherche, filtre par catégorie, tri."""
    products = Product.objects.filter(available=True).select_related("category")

    query = request.GET.get("q", "").strip()
    category_slug = request.GET.get("category", "").strip()
    sort = request.GET.get("sort", "").strip()
    gender = request.GET.get("gender", "").strip()

    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    current_category = None
    if category_slug:
        current_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=current_category)

    if gender:
        products = products.filter(gender=gender)

    sort_map = {
        "price_asc": "price",
        "price_desc": "-price",
        "newest": "-created_at",
        "oldest": "created_at",
        "name": "name",
    }
    products = products.order_by(sort_map.get(sort, "-created_at"))

    paginator = Paginator(products, 9)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "page_obj": page_obj,
        "products": page_obj.object_list,
        "categories": Category.objects.all(),
        "current_category": current_category,
        "query": query,
        "sort": sort,
        "gender": gender,
    }
    return render(request, "products/product_list.html", context)


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.select_related("category"), slug=slug
    )
    reviews = product.reviews.select_related("user")

    # Recommandation IA : produits similaires via TF-IDF + similarité cosinus.
    related = get_recommendations(product, k=4)
    # Repli sur la même catégorie si le moteur ne renvoie rien.
    if not related:
        related = list(
            Product.objects.filter(available=True, category=product.category)
            .exclude(pk=product.pk)
            .order_by("-created_at")[:4]
        )

    user_review = None
    if request.user.is_authenticated:
        user_review = reviews.filter(user=request.user).first()

    review_form = ReviewForm(instance=user_review)

    context = {
        "product": product,
        "reviews": reviews,
        "related": related,
        "review_form": review_form,
        "user_review": user_review,
    }
    return render(request, "products/product_detail.html", context)


@login_required
def add_review(request, slug):
    product = get_object_or_404(Product, slug=slug)
    if request.method == "POST":
        instance = product.reviews.filter(user=request.user).first()
        form = ReviewForm(request.POST, instance=instance)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            messages.success(request, "Merci, votre avis a été enregistré.")
        else:
            messages.error(request, "Veuillez corriger les erreurs du formulaire.")
    return redirect("products:product_detail", slug=slug)
