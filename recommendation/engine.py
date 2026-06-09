"""Système de recommandation de produits basé sur le contenu.

Principe (content-based filtering) :
1. Chaque produit est transformé en un « document » texte
   (nom + catégorie + description).
2. On **entraîne** un vectoriseur **TF-IDF** sur un échantillon de 20 %
   des produits (apprentissage du vocabulaire et des poids IDF).
3. On projette ensuite *tous* les produits dans cet espace TF-IDF et on
   calcule la **similarité cosinus** entre eux.
4. Pour un produit donné, on retourne les produits les plus proches.

Implémentation : scikit-learn (TfidfVectorizer + cosine_similarity).
"""

import random

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from products.models import Product

# Fraction du dataset utilisée pour entraîner le vectoriseur TF-IDF.
TRAIN_FRACTION = 0.2
RANDOM_SEED = 42

# Liste réduite de mots vides français (scikit-learn ne fournit que l'anglais).
FRENCH_STOP_WORDS = [
    "le", "la", "les", "un", "une", "des", "de", "du", "et", "ou", "à", "au",
    "aux", "en", "dans", "sur", "pour", "par", "avec", "sans", "ce", "cet",
    "cette", "ces", "son", "sa", "ses", "leur", "leurs", "il", "elle", "ils",
    "elles", "on", "nous", "vous", "qui", "que", "quoi", "dont", "est", "sont",
    "plus", "très", "tout", "tous", "toute", "toutes", "pas", "ne", "se", "sa",
    "comme", "mais", "donc", "car", "votre", "vos", "notre", "nos", "vente",
]


class ProductRecommender:
    """Modèle de recommandation construit à partir du catalogue."""

    def __init__(self):
        self._products = []
        self._index = {}          # product_id -> position dans la matrice
        self._similarity = None   # matrice de similarité cosinus
        self.train_size = 0       # nombre de produits utilisés à l'entraînement
        self.vocab_size = 0       # taille du vocabulaire TF-IDF appris

    @staticmethod
    def _document(product):
        """Construit le document texte d'un produit.

        On répète le nom et la catégorie pour leur donner plus de poids
        que la description seule.
        """
        category = product.category.name if product.category_id else ""
        return " ".join(
            [
                product.name,
                product.name,
                category,
                category,
                product.description or "",
            ]
        )

    def fit(self, products, train_fraction=TRAIN_FRACTION):
        """Entraîne le modèle.

        Le vectoriseur TF-IDF est *entraîné* (``fit``) sur un échantillon
        aléatoire de ``train_fraction`` des produits (20 % par défaut), puis
        *tous* les produits sont projetés (``transform``) dans cet espace pour
        calculer la similarité cosinus servie sur le site.
        """
        self._products = list(products)
        self._index = {p.id: i for i, p in enumerate(self._products)}

        # Au moins 2 produits sont nécessaires pour mesurer une similarité.
        if len(self._products) < 2:
            self._similarity = None
            return self

        corpus = [self._document(p) for p in self._products]

        # Échantillon d'entraînement : 20 % des lignes (au moins 2).
        n = len(corpus)
        train_n = max(2, int(round(n * train_fraction)))
        rng = random.Random(RANDOM_SEED)
        train_indices = rng.sample(range(n), min(train_n, n))
        train_corpus = [corpus[i] for i in train_indices]

        vectorizer = TfidfVectorizer(
            stop_words=FRENCH_STOP_WORDS,
            lowercase=True,
            ngram_range=(1, 2),
        )
        # Apprentissage du vocabulaire + IDF sur l'échantillon (20 %).
        vectorizer.fit(train_corpus)
        # Projection de l'ensemble du catalogue dans l'espace appris.
        tfidf_matrix = vectorizer.transform(corpus)

        self._similarity = cosine_similarity(tfidf_matrix)
        self.train_size = len(train_corpus)
        self.vocab_size = len(vectorizer.vocabulary_)
        return self

    def recommend(self, product, k=4):
        """Retourne les `k` produits les plus similaires à `product`."""
        if self._similarity is None or product.id not in self._index:
            return []

        position = self._index[product.id]
        scores = list(enumerate(self._similarity[position]))

        # Tri par similarité décroissante, en excluant le produit lui-même.
        scores.sort(key=lambda x: x[1], reverse=True)
        recommended = []
        for idx, score in scores:
            if idx == position or score <= 0:
                continue
            recommended.append(self._products[idx])
            if len(recommended) >= k:
                break
        return recommended


# --- Cache mémoire simple -------------------------------------------------
# On évite de reconstruire le modèle à chaque requête : il n'est recalculé
# que lorsque le catalogue change (nombre de produits ou dernière mise à jour).

_recommender = None
_signature = None


def _catalog_signature(queryset):
    from django.db.models import Max

    agg = queryset.aggregate(last=Max("updated_at"))
    return (queryset.count(), agg["last"])


def get_recommendations(product, k=4):
    """Point d'entrée : recommandations pour un produit (avec cache)."""
    global _recommender, _signature

    queryset = Product.objects.filter(available=True).select_related("category")
    signature = _catalog_signature(queryset)

    if _recommender is None or signature != _signature:
        _recommender = ProductRecommender().fit(queryset)
        _signature = signature

    return _recommender.recommend(product, k=k)


def reset_cache():
    """Force la reconstruction du modèle au prochain appel (utile en test)."""
    global _recommender, _signature
    _recommender = None
    _signature = None
