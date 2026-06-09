#!/bin/sh
set -e

# Attend que PostgreSQL soit prêt (si configuré).
if [ -n "$DB_HOST" ]; then
    echo "En attente de la base de données ($DB_HOST:$DB_PORT)..."
    while ! nc -z "$DB_HOST" "${DB_PORT:-5432}"; do
        sleep 0.5
    done
    echo "Base de données disponible."
fi

echo "Application des migrations..."
python manage.py migrate --noinput

# Migration des données initiales : charge datadump.json (export complet de
# l'ancienne base SQLite : utilisateurs, profils, paniers, commandes, produits)
# uniquement si la base est vide. Idempotent => un redémarrage ne recharge pas
# (et n'écrase donc aucune donnée saisie depuis).
echo "Vérification des données initiales..."
USER_COUNT=$(python manage.py shell -c "from django.contrib.auth.models import User; print(User.objects.count())" 2>/dev/null | tail -n1)

if [ "$USER_COUNT" = "0" ] || [ -z "$USER_COUNT" ]; then
    if [ -f /app/datadump.json ]; then
        echo "Base vide : chargement de datadump.json..."
        python manage.py loaddata /app/datadump.json
    else
        echo "datadump.json introuvable : import du catalogue depuis fashion.csv..."
        python manage.py import_fashion
    fi
else
    echo "Données déjà présentes ($USER_COUNT utilisateurs), chargement ignoré."
fi

echo "Collecte des fichiers statiques..."
python manage.py collectstatic --noinput

exec "$@"
