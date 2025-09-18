# Scripts Conciergerie Cordo

Scripts utilitaires pour la configuration et les tests de l'application.

## 🚀 **Scripts de configuration**

### `dev-setup.sh`
**Configuration complète de l'environnement de développement**

```bash
./scripts/dev-setup.sh
```

- Démarre les conteneurs Docker
- Initialise la base de données
- Seed les données initiales
- Prêt pour le développement !

### `setup-gcs.sh`
**Configuration automatique de Google Cloud Storage**

```bash
./scripts/setup-gcs.sh
```

- Crée le projet `conciergerie-cordo`
- Crée le bucket `conciergerie-cordo-photos`
- Configure le service account
- Génère la clé JSON
- Met à jour le fichier `.env`

## 🧪 **Scripts de test**

### `test_email.py`
**Test de la configuration email Gmail**

```bash
./scripts/test_email.py
```

- Vérifie la configuration SMTP
- Envoie un email de test
- Valide les credentials Gmail

### `test_gcs.py`
**Test de Google Cloud Storage**

```bash
./scripts/test_gcs.py
```

- Vérifie la configuration GCS
- Test d'upload d'image
- Test des URLs signées
- Nettoyage automatique

## 📋 **Ordre d'exécution recommandé**

### **Première installation :**

1. **Configuration Google Cloud** (si souhaité)
   ```bash
   ./scripts/setup-gcs.sh
   ```

2. **Configuration environnement complet**
   ```bash
   ./scripts/dev-setup.sh
   ```

3. **Tests de validation**
   ```bash
   ./scripts/test_email.py
   ./scripts/test_gcs.py
   ```

### **Développement quotidien :**

```bash
# Démarrer l'application
docker-compose up

# Ou utiliser le script
./scripts/dev-setup.sh
```

## 🔧 **Prérequis**

### Pour `setup-gcs.sh` :
- Google Cloud CLI installé (`brew install google-cloud-sdk`)
- Authentification Google Cloud (`gcloud auth login`)
- Facturation activée sur Google Cloud

### Pour `dev-setup.sh` :
- Docker et Docker Compose
- Fichier `.env` configuré

### Pour les tests :
- Configuration correspondante dans `.env`
- Dépendances Python installées

## 💡 **Conseils**

- **Permissions** : Tous les scripts sont exécutables (`chmod +x`)
- **Logs** : Les scripts affichent des messages détaillés
- **Erreurs** : Codes de sortie appropriés pour l'automatisation
- **Sécurité** : Aucun secret affiché dans les logs

## 🆘 **Dépannage**

### Erreurs communes :

1. **Script non exécutable**
   ```bash
   chmod +x scripts/*.sh scripts/*.py
   ```

2. **Docker non disponible**
   ```bash
   # Vérifier Docker
   docker --version
   docker-compose --version
   ```

3. **Google Cloud non configuré**
   ```bash
   # Installer et configurer
   brew install google-cloud-sdk
   gcloud auth login
   ```

4. **Variables d'environnement manquantes**
   ```bash
   # Copier le template
   cp .env.development .env
   # Puis éditer .env
   ```