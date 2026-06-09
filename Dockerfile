FROM python:3.11-slim

# Bonnes pratiques Python en conteneur
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Dépendances système (psycopg2, Pillow)
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Installation des dépendances Python (couche cachée tant que requirements ne change pas)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Code de l'application
COPY . .

# Script d'entrée (migrations + collectstatic + démarrage)
RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "ecommerce_project.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
