# Conciergerie Cordo

Site web pour une cordonnerie offrant ses services en conciergerie pour des entreprises dans la CUB bordelaise.

## Fonctionnalités

- 🏠 **Page d'accueil** - Présentation des services et zones couvertes
- 📱 **Commande mobile** - Interface optimisée mobile avec prise de photo
- 💳 **Paiement Stripe** - Checkout sécurisé avec Stripe
- 📧 **Emails automatiques** - Confirmations client et notifications admin
- ☁️ **Stockage cloud** - Photos stockées sur Google Cloud Storage
- 🚀 **Déploiement Fly.io** - Configuration prête pour la production

## Architecture

- **Backend**: Flask + SQLAlchemy + PostgreSQL
- **Frontend**: HTML/CSS/JS + Bootstrap 5 (Mobile-first)
- **Paiement**: Stripe Checkout
- **Stockage**: Google Cloud Storage
- **Email**: SMTP (SendGrid/Mailgun)
- **Déploiement**: Fly.io

## Installation et développement

### Prérequis

- Python 3.11+
- Docker et Docker Compose
- PostgreSQL (fourni via Docker)

### Démarrage rapide

1. **Cloner le projet**
   ```bash
   git clone <repository-url>
   cd conciergerie-cordo
   ```

2. **Configuration automatique**
   ```bash
   # Script de configuration complète
   ./scripts/dev-setup.sh
   ```

3. **Accéder à l'application**
   - http://localhost:5000

### Développement local sans Docker

1. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configurer PostgreSQL**
   ```bash
   # Installer PostgreSQL localement ou utiliser Docker
   docker run --name postgres-cordo -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres:15
   ```

3. **Variables d'environnement**
   ```bash
   export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/conciergerie_cordo"
   export FLASK_ENV="development"
   export SECRET_KEY="your-dev-secret-key"
   ```

4. **Migrations et données**
   ```bash
   flask db upgrade
   python seed_data.py
   ```

5. **Démarrer l'application**
   ```bash
   python app.py
   ```

## Configuration

### Variables d'environnement

Créez un fichier `.env` basé sur `.env.example`:

```bash
# Base de données
DATABASE_URL=postgresql://user:password@host:port/database

# Stripe (obligatoire pour les paiements)
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Google Cloud Storage (obligatoire)
GOOGLE_CLOUD_PROJECT_ID=conciergerie-cordo
GCS_BUCKET_NAME=conciergerie-cordo-photos
GOOGLE_APPLICATION_CREDENTIALS=/path/to/gcs-service-account.json

# Email Gmail SMTP
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=votre-email@gmail.com
SMTP_PASSWORD=votre_mot_de_passe_application
FROM_EMAIL=contact@conciergeriecordo.com
ADMIN_EMAIL=admin@conciergeriecordo.com

# Flask
SECRET_KEY=your-secret-key
DOMAIN=conciergeriecordo.com
```

### Configuration Stripe

1. Créer un compte Stripe
2. Récupérer les clés API (mode test pour le développement)
3. Configurer un webhook pour `payment_intent.succeeded` et `payment_intent.payment_failed`
4. URL du webhook: `https://yourdom.com/webhook/stripe`

### Configuration Google Cloud Storage

1. Créer un projet Google Cloud
2. Activer l'API Cloud Storage
3. Créer un bucket
4. Créer un compte de service avec les permissions Storage Admin
5. Télécharger le fichier JSON des credentials

### Configuration Email

1. Créer un compte SendGrid ou Mailgun
2. Récupérer les credentials SMTP
3. Configurer les variables d'environnement

## Structure du projet

```
conciergerie-cordo/
├── app.py                    # Application Flask principale
├── config.py                 # Configuration environnements
├── requirements.txt          # Dépendances Python
├── seed_data.py             # Script d'initialisation des données
├── docker-compose.yml       # Configuration Docker dev
├── Dockerfile              # Image production
├── fly.toml                # Configuration Fly.io
├── models/                 # Modèles SQLAlchemy
│   ├── commandes.py
│   ├── paires.py
│   └── prestations.py
├── routes/                 # Routes Flask
│   ├── main.py
│   └── api.py
├── services/               # Services (email, storage)
│   ├── email.py
│   └── storage.py
├── templates/              # Templates HTML
│   ├── base.html
│   ├── home.html
│   ├── choix_prestation.html
│   └── checkout.html
├── static/                 # Assets statiques
│   ├── css/
│   ├── js/
│   └── img/
├── migrations/             # Migrations Alembic
└── uploads/               # Stockage local temporaire
```

## API Endpoints

### Publics
- `GET /` - Page d'accueil
- `GET /choix-prestation` - Page de commande
- `GET /checkout` - Résultat du paiement
- `POST /webhook/stripe` - Webhook Stripe

### API
- `GET /api/prestations` - Liste des prestations
- `GET /api/prestations/<type>` - Prestations par type
- `POST /api/upload-photo` - Upload d'une photo
- `POST /api/commande` - Créer une commande
- `POST /api/commande/<id>/checkout` - Créer session Stripe
- `GET /api/commande/<id>` - Détails d'une commande

## Déploiement

### Fly.io

1. **Installer Fly CLI**
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Authentification**
   ```bash
   fly auth login
   ```

3. **Déployer**
   ```bash
   fly deploy
   ```

4. **Configurer les variables d'environnement**
   ```bash
   fly secrets set STRIPE_SECRET_KEY=sk_live_...
   fly secrets set DATABASE_URL=postgresql://...
   # etc.
   ```

5. **Initialiser la base de données**
   ```bash
   fly ssh console
   python seed_data.py
   ```

### Base de données production

Fly.io propose PostgreSQL managé:

```bash
fly postgres create
fly postgres attach <postgres-app-name>
```

## Tests

```bash
# Test email Gmail
./scripts/test_email.py

# Test Google Cloud Storage
./scripts/test_gcs.py

# Tests d'intégration
curl http://localhost:5000/api/prestations
```

## Maintenance

### Migrations

```bash
# Créer une migration
flask db migrate -m "Description"

# Appliquer les migrations
flask db upgrade
```

### Logs

```bash
# Logs Fly.io
fly logs

# Logs Docker
docker-compose logs web
```

### Backup base de données

```bash
# Backup local
pg_dump $DATABASE_URL > backup.sql

# Restore
psql $DATABASE_URL < backup.sql
```

## Support

- Email: contact@conciergeriecordo.com
- Documentation technique: voir `/docs/`

## Licence

Propriétaire - Conciergerie Cordo