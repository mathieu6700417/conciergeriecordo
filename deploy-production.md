# Déploiement Production - Conciergerie Cordo

## 🚀 Configuration Fly.io

### 1. Prérequis

- Installer Fly CLI : https://fly.io/docs/hands-on/install-flyctl/
- Se connecter : `fly auth login`
- Créer l'application : `fly launch` (si pas déjà fait)

### 2. Configuration des secrets

Les secrets sont automatiquement synchronisés depuis `.env.production`.

#### Configuration initiale

1. **Copier et configurer le fichier d'environnement :**
   ```bash
   cp .env.example .env.production
   ```

2. **Éditer `.env.production` avec vos vraies valeurs :**
   - Clés Stripe de production
   - Configuration email SMTP
   - Secret key Flask sécurisé
   - Credentials Google Cloud Storage

3. **Synchroniser avec Fly.io :**
   ```bash
   ./scripts/sync-fly-secrets.sh
   ```

   Ce script va automatiquement :
   - Lire toutes les variables de `.env.production`
   - Les configurer comme secrets sur Fly.io
   - Ignorer les valeurs par défaut (contenant "YOUR", "your", "...")

### 3. Base de données PostgreSQL

```bash
# Créer une base PostgreSQL sur Fly.io
fly postgres create

# Attacher la base à l'application
fly postgres attach <nom-de-votre-db>

# La variable DATABASE_URL sera automatiquement configurée
```

### 4. Google Cloud Storage

1. Créer un compte de service sur Google Cloud Console
2. Télécharger le fichier JSON de credentials
3. Encoder le fichier en base64 :
   ```bash
   base64 -i gcs-service-account.json | tr -d '\n' > gcs-encoded.txt
   ```
4. Ajouter le contenu encodé dans `.env.production` :
   ```
   GOOGLE_APPLICATION_CREDENTIALS_BASE64=<contenu-encodé>
   ```
5. Re-synchroniser : `./scripts/sync-fly-secrets.sh`

### 5. Déploiement

```bash
# Déployer l'application
fly deploy

# Vérifier le statut
fly status

# Voir les logs
fly logs

# Ouvrir l'application
fly open
```

### 6. Webhooks Stripe

1. Aller sur https://dashboard.stripe.com/webhooks
2. Créer un nouveau webhook avec l'URL : `https://votre-app.fly.dev/api/stripe/webhook`
3. Sélectionner les événements : `checkout.session.completed`
4. Copier le webhook secret
5. Mettre à jour `.env.production` avec le secret
6. Re-synchroniser : `./scripts/sync-fly-secrets.sh`

### 7. Commandes utiles

```bash
# Re-synchroniser les secrets après modification de .env.production
./scripts/sync-fly-secrets.sh

# Voir les secrets configurés (sans les valeurs)
fly secrets list

# Supprimer un secret
fly secrets unset NOM_DU_SECRET

# SSH dans le container
fly ssh console

# Exécuter les migrations
fly ssh console -C "flask db upgrade"

# Redémarrer l'application
fly apps restart
```

### 8. Monitoring

```bash
# Voir les métriques
fly dashboard metrics

# Configurer les alertes (dans fly.toml)
# Voir la documentation : https://fly.io/docs/reference/metrics/
```

## 🔒 Sécurité

- **Ne jamais commiter `.env.production` avec des vraies valeurs**
- Utiliser des secrets forts et uniques
- Activer 2FA sur tous les services (Stripe, Google Cloud, Fly.io)
- Régulièrement mettre à jour les dépendances : `pip list --outdated`

## 📝 Notes

- Les secrets Fly.io sont chiffrés et ne peuvent pas être lus après configuration
- Pour voir une valeur, vous devez la re-définir
- Les changements de secrets nécessitent un redéploiement : `fly deploy`