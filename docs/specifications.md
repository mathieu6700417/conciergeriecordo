# Spécifications - Conciergerie Cordo

## Vue d'ensemble

Site web pour une cordonnerie offrant ses services en conciergerie pour des entreprises dans la CUB bordelaise (Bordeaux, Pessac, Talence, Mérignac, Bègles, Villenave d'Ornon)

**Domaine** : conciergeriecordo.com (Namecheap)
**Déploiement** : Fly.io avec PostgreSQL existant

## Fonctionnalités principales

### 1. Page d'accueil (/)
- Présentation des services de cordonnerie
- Zones couvertes : CUB bordelaise (Bordeaux, Pessac, Talence, Mérignac, Bègles, Villenave d'Ornon)
- Informations sur le service de conciergerie de coordonnerie pour les entreprises

### 2. Page de commande (/choix-prestation)
**Accessible via QR code sur flyers**

#### Étapes de commande :
1. **Ajout de paires** :
   - Ajouter une ou plusieurs paires de chaussures
   - Pour chaque paire :
     - Prendre une photo de la paire (obligatoire)
     - Choisir sexe : Homme / Femme
     - Sélectionner un ou plusieurs services :
       - Patin
       - Talon
       - Patin Gomme
       - Talon Gomme
       - Resemmelage complet basket

2. **Validation** : Récapitulatif détaillé par paire et services

3. **Checkout** : Formulaire client (nom, email, téléphone, entreprise) + paiement Stripe

## Architecture technique

### Stack
- **Backend** : Flask + SQLAlchemy
- **Base de données** : PostgreSQL (Fly.io existant)
- **Stockage photos** : Google Cloud Storage
- **Frontend** : HTML/CSS/JS + Bootstrap 5 (Mobile-first)
- **Paiement** : Stripe Checkout
- **Développement** : Docker + docker-compose
- **Déploiement** : Fly.io

### Structure du projet
```
conciergerie-cordo/
├── Dockerfile                # Image production
├── docker-compose.yml        # Dev local avec PostgreSQL
├── .env.example              # Variables d'environnement
├── .dockerignore
├── app.py                    # Application Flask principale
├── requirements.txt          # Dépendances Python
├── fly.toml                  # Configuration Fly.io
├── docs/                     # Documentation
│   └── specifications.md     # Ce fichier
├── models/                   # Modèles SQLAlchemy
│   ├── __init__.py
│   ├── commande.py          # Modèle commandes
│   ├── paire.py             # Modèle paires de chaussures
│   └── prestation.py        # Modèle prestations
├── routes/                   # Routes organisées
│   ├── __init__.py
│   ├── main.py              # Routes principales
│   └── api.py               # API endpoints
├── templates/                # Templates HTML
│   ├── base.html            # Template de base responsive
│   ├── home.html            # Page d'accueil
│   ├── choix_prestation.html # Page QR code
│   └── checkout.html        # Page paiement
├── static/                   # Assets statiques
│   ├── css/
│   │   ├── main.css         # Styles principaux
│   │   └── mobile.css       # Optimisations mobile
│   ├── js/
│   │   ├── main.js          # JavaScript principal
│   │   ├── commande.js      # Logic page commande
│   │   └── camera.js        # Gestion caméra/photos
│   └── img/                 # Images et logos
├── migrations/               # Migrations Alembic
└── config.py                # Configuration environnements
```

## Base de données

### Tables principales

#### prestations
```sql
id (PK)
nom (VARCHAR)
prix (DECIMAL)
type_chaussure (ENUM: homme, femme)
description (TEXT)
actif (BOOLEAN)
created_at (TIMESTAMP)
```

#### commandes
```sql
id (PK)
nom (VARCHAR)
email (VARCHAR)
telephone (VARCHAR)
entreprise (VARCHAR)
statut (ENUM: pending, paid, processing, completed, cancelled)
total (DECIMAL)
stripe_payment_intent_id (VARCHAR)
created_at (TIMESTAMP)
updated_at (TIMESTAMP)
```

#### paires
```sql
id (PK)
commande_id (FK)
type_chaussure (ENUM: homme, femme)
photo_url (VARCHAR)     # URL Google Cloud Storage
photo_gcs_path (VARCHAR) # Chemin dans le bucket GCS
photo_filename (VARCHAR) # Nom original du fichier
description (TEXT)      # Description optionnelle de la paire
ordre (INTEGER)         # Ordre d'affichage dans la commande
created_at (TIMESTAMP)
```

#### paire_prestations
```sql
id (PK)
paire_id (FK)
prestation_id (FK)
prix_unitaire (DECIMAL)
created_at (TIMESTAMP)
```

## Interface utilisateur

### Design responsive (Mobile-first)
- **Framework** : Bootstrap 5
- **Breakpoints** : Mobile (320px+) → Tablet (768px+) → Desktop (1024px+)
- **Navigation** : Tactile optimisée, boutons ≥ 44px
- **Performance** : Images responsives, lazy loading, CSS/JS minifiés

### Pages clés

#### Page d'accueil
- Hero section avec présentation du service
- Section services avec visuels
- Section zones couvertes avec carte ou liste
- Témoignages clients (optionnel)
- Footer avec contact et mentions légales

#### Page de commande (/choix-prestation)
- Interface simple et intuitive
- Gestion des paires de chaussures :
  - Prise de photo obligatoire (caméra mobile ou upload)
  - Ajout/suppression de paires
  - Sélection type (homme/femme) par paire
  - Multi-sélection de services par paire
- Récapitulatif en temps réel avec détail par paire
- Boutons d'action clairs et visibles

#### Page checkout
- Formulaire client :
  - Nom complet (obligatoire)
  - Email (obligatoire)
  - Numéro de téléphone (obligatoire)
  - Entreprise (obligatoire)
- Intégration Stripe Elements
- Récapitulatif détaillé :
  - Liste des paires avec photo et services
  - Sous-totaux par paire
  - Total général
- Confirmation de paiement

## Environnements

### Développement local
```bash
# Démarrer l'environnement
docker-compose up

# Accès
- Application : http://localhost:5000
- PostgreSQL : localhost:5432
```

### Production (Fly.io)
- Utilisation du PostgreSQL Fly.io existant
- Variables d'environnement pour Stripe
- Configuration domaine custom
- HTTPS automatique

## Variables d'environnement

```bash
# Base de données
DATABASE_URL=postgresql://...

# Stripe
STRIPE_PUBLISHABLE_KEY=pk_...
STRIPE_SECRET_KEY=sk_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Google Cloud Storage
GOOGLE_CLOUD_PROJECT_ID=conciergerie-cordo
GCS_BUCKET_NAME=conciergerie-cordo-photos
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

# Email
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=...
FROM_EMAIL=contact@conciergeriecordo.com
ADMIN_EMAIL=admin@conciergeriecordo.com

# Flask
FLASK_ENV=production
SECRET_KEY=...

# Application
DOMAIN=conciergeriecordo.com
```

## Commandes de développement

```bash
# Démarrer en local
docker-compose up

# Migrations
docker-compose exec web flask db upgrade

# Shell interactif
docker-compose exec web flask shell

# Tests (à implémenter)
docker-compose exec web pytest
```

## Intégration Stripe

### Flux de paiement
1. Client valide sa commande
2. Création Payment Intent Stripe
3. Redirection vers Stripe Checkout
4. Webhook de confirmation
5. Mise à jour statut commande
6. Email de confirmation automatique

### Webhooks
- `payment_intent.succeeded` : Commande payée → envoi email confirmation
- `payment_intent.payment_failed` : Échec paiement → envoi email échec

### Emails automatiques

#### Email de confirmation de commande (Client)
**Déclenché** : Webhook `payment_intent.succeeded`
**Destinataire** : Email client saisi lors du checkout
**Contenu** :
- Numéro de commande unique
- Récapitulatif des paires et services
- Photos des paires
- Total payé
- Coordonnées de contact (téléphone entreprise)
- Délai estimatif de traitement
- Informations de récupération

#### Email de notification admin (Cordonnerie)
**Déclenché** : Webhook `payment_intent.succeeded`
**Destinataire** : Email admin cordonnerie
**Contenu** :
- **NOUVELLE COMMANDE** en objet
- Numéro de commande unique
- Informations client (nom, email, téléphone, entreprise)
- Détail par paire :
  - Photo haute résolution
  - Type (homme/femme)
  - Services demandés avec prix
  - Sous-total par paire
- Total de la commande
- Date et heure de commande
- Lien vers interface admin (futur)

#### Email d'échec de paiement
**Déclenché** : Webhook `payment_intent.payment_failed`
**Contenu** :
- Raison de l'échec
- Lien pour recommencer le paiement
- Support client

#### Configuration email
**Service** : SMTP (ex: SendGrid, Mailgun)
**Templates** : HTML responsive + version texte
**Variables d'environnement** :
```bash
SMTP_HOST=...
SMTP_PORT=587
SMTP_USER=...
SMTP_PASSWORD=...
FROM_EMAIL=contact@conciergeriecordo.com
ADMIN_EMAIL=admin@conciergeriecordo.com
```

## Déploiement

### Première fois
```bash
# Configuration Fly.io
fly deploy

# Configuration base de données
fly ssh console -a app-name
flask db upgrade
```

### Mises à jour
```bash
fly deploy
```

## Gestion des photos

### Upload et stockage
- **Format** : JPEG/PNG, max 5MB par photo
- **Stockage** : Google Cloud Storage bucket
- **Structure** : `photos/{année}/{mois}/{commande_id}/{paire_id}_{timestamp}.jpg`
- **Nettoyage** : Suppression automatique des photos des commandes annulées
- **Sécurité** : Validation type MIME, redimensionnement automatique
- **URLs signées** : Accès temporaire sécurisé aux photos

### Interface caméra
- **API WebRTC** : accès caméra sur mobile/desktop
- **Fallback** : input file si caméra indisponible
- **Preview** : aperçu avant validation
- **Compression** : réduction taille avant upload GCS
- **Upload progressif** : indicateur de progression
- **Retry automatique** : en cas d'échec réseau

## Évolutions futures possibles
- Panel admin pour gérer les commandes
- Notifications SMS/Email automatiques
- Système de suivi de commande
- API mobile
- Intégration calendrier pour les livraisons
- Reconnaissance automatique type de chaussure par IA
