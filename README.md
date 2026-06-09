# E-Shop Django 🛒

Plateforme e-commerce moderne développée avec **Django** — projet de fin de module
(développement, sécurisation et déploiement). Domaine choisi : **boutique de chaussures**
(dataset Myntra `fashion.csv`, sous-catégorie *Shoes*). Le catalogue est organisé par
**type de chaussure** (Casual, Sports, Heels, Flats, Formal) et séparé **Homme / Femme**.

## Fonctionnalités

- **Comptes & rôles** : visiteur, client (authentifié), administrateur/gestionnaire.
- **Catalogue** : grille de produits, recherche par mot-clé, filtre par catégorie,
  tri par prix / date / nom, pagination.
- **Panier** : ajout, modification des quantités, suppression, vidage, total.
- **Commandes** : validation (checkout), historique, suivi du statut
  (en attente, confirmée, en préparation, expédiée, livrée, annulée), décrément du stock.
- **Avis clients** : note (1–5 étoiles) + commentaire, note moyenne par produit.
- **Tableau de bord admin** : nombre de produits/clients/commandes, chiffre d'affaires,
  meilleures ventes, commandes récentes, répartition par statut, alertes de stock faible.
- **Administration Django** complète pour la gestion CRUD.
- **Page d'accueil** : hero, types de chaussures, et deux rayons **Chaussures Homme**
  et **Chaussures Femme** (filtre `?gender=Men|Women` également dans le catalogue).
- **Module IA** (`recommendation/`) : système de recommandation **content-based**.
  Le vectoriseur **TF-IDF** est *entraîné sur 20 % des produits* (apprentissage du
  vocabulaire + IDF), puis tout le catalogue est projeté dans cet espace et comparé
  par **similarité cosinus** (scikit-learn). Affiché sur la fiche produit
  (« Vous aimerez aussi »). Le modèle se ré-entraîne automatiquement après un import.

## Architecture

```
ecommerce_project/   # configuration du projet (settings, urls, wsgi)
accounts/            # utilisateurs, inscription, connexion, profils
products/            # produits, catégories, recherche, filtres, avis
cart/                # panier d'achat
orders/              # commandes et checkout
dashboard/           # statistiques et administration
recommendation/      # fonctionnalité IA (à implémenter)
templates/  static/  media/
Dockerfile  docker-compose.yml  nginx/  .github/workflows/
```

## Technologies

Django 5 · PostgreSQL · Bootstrap 5 · Gunicorn · WhiteNoise · Nginx · Docker · GitHub Actions.

## Démarrage en local (sans Docker)

```bash
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/Mac
pip install -r requirements.txt

copy .env.example .env         # puis adaptez les valeurs (SQLite par défaut)

python manage.py migrate
python manage.py import_fashion   # importe fashion.csv (50 produits / catégorie)
python manage.py createsuperuser
python manage.py runserver
```

Application : http://127.0.0.1:8000 — Admin : http://127.0.0.1:8000/admin

## Démarrage avec Docker Compose

```bash
copy .env.example .env         # renseignez DB_NAME, DB_USER, DB_PASSWORD, DB_HOST=db
docker compose up --build
```

L'application est servie par **Nginx** sur http://localhost (Gunicorn + PostgreSQL en arrière-plan).

## Tests

```bash
python manage.py test
```

## CI/CD

Le workflow [`.github/workflows/ci-cd.yml`](.github/workflows/ci-cd.yml) :
installe les dépendances, vérifie la qualité du code (flake8), lance les migrations
et les tests sur PostgreSQL, puis construit et publie l'image Docker sur GHCR
(à chaque push sur `main`).

## Sécurité

- Authentification requise pour le panier, le checkout et les avis.
- Mots de passe gérés/hashés par Django, validateurs de mot de passe activés.
- Protection CSRF active, validation des formulaires côté serveur.
- Espaces administrateur protégés (`is_staff`).
- Variables sensibles dans `.env` (jamais commité), `DEBUG=False` en production,
  cookies sécurisés, HSTS et autres en-têtes de sécurité activés hors debug.
- Taille des fichiers uploadés limitée.

## Comptes de démonstration

| Rôle  | Identifiant | Mot de passe |
|-------|-------------|--------------|
| Admin | `admin`     | `admin12345` |

> ⚠️ Le fichier `.env` ne doit **jamais** être publié sur GitHub.
