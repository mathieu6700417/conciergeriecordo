# Configuration Google Cloud Storage - Conciergerie Cordo

## 🚀 **Étapes de configuration complète**

### **1. Installer Google Cloud CLI**

```bash
# macOS
brew install google-cloud-sdk

# Ou télécharger depuis: https://cloud.google.com/sdk/docs/install

# Linux/WSL
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

### **2. Authentification et configuration initiale**

```bash
# Se connecter à Google Cloud
gcloud auth login

# Lister vos projets existants
gcloud projects list

# Définir la région par défaut (Europe)
gcloud config set compute/region europe-west1
gcloud config set compute/zone europe-west1-b
```

### **3. Créer le projet Conciergerie Cordo**

```bash
# Créer le projet
gcloud projects create conciergerie-cordo \
  --name="Conciergerie Cordo" \
  --set-as-default

# Activer la facturation (requis pour Cloud Storage)
# Vous devrez faire cela dans la console: https://console.cloud.google.com/billing
```

### **4. Activer les APIs nécessaires**

```bash
# Activer Cloud Storage API
gcloud services enable storage.googleapis.com

# Activer IAM API
gcloud services enable iam.googleapis.com

# Vérifier les services activés
gcloud services list --enabled
```

### **5. Créer le bucket Cloud Storage**

```bash
# Créer le bucket
gcloud storage buckets create gs://conciergerie-cordo-photos \
  --location=europe-west1 \
  --storage-class=STANDARD \
  --uniform-bucket-level-access

# Configurer les permissions publiques pour les photos
gcloud storage buckets add-iam-policy-binding gs://conciergerie-cordo-photos \
  --member=allUsers \
  --role=roles/storage.objectViewer
```

### **6. Créer le compte de service**

```bash
# Créer le compte de service
gcloud iam service-accounts create conciergerie-cordo-storage \
  --display-name="Conciergerie Cordo Storage Service" \
  --description="Service account for Conciergerie Cordo photo storage"

# Attribuer les permissions Storage Admin
gcloud projects add-iam-policy-binding conciergerie-cordo \
  --member="serviceAccount:conciergerie-cordo-storage@conciergerie-cordo.iam.gserviceaccount.com" \
  --role="roles/storage.admin"

# Créer et télécharger la clé JSON
gcloud iam service-accounts keys create ~/conciergerie-cordo-service-account.json \
  --iam-account=conciergerie-cordo-storage@conciergerie-cordo.iam.gserviceaccount.com
```

### **7. Configurer l'application**

```bash
# Copier la clé dans le projet
cp ~/conciergerie-cordo-service-account.json ./gcs-service-account.json

# Mettre à jour .env
echo "GOOGLE_CLOUD_PROJECT_ID=conciergerie-cordo" >> .env
echo "GCS_BUCKET_NAME=conciergerie-cordo-photos" >> .env
echo "GOOGLE_APPLICATION_CREDENTIALS=$(pwd)/gcs-service-account.json" >> .env
```

## 🧪 **Tester la configuration**

### **1. Script de test GCS**

```python
# test_gcs.py
from google.cloud import storage
import os

def test_gcs():
    client = storage.Client()
    bucket_name = os.getenv('GCS_BUCKET_NAME')
    bucket = client.bucket(bucket_name)

    # Test upload
    blob = bucket.blob('test/hello.txt')
    blob.upload_from_string('Hello from Conciergerie Cordo!')
    blob.make_public()

    print(f"✅ Test file uploaded: {blob.public_url}")

    # Cleanup
    blob.delete()
    print("✅ Test file deleted")

if __name__ == '__main__':
    test_gcs()
```

### **2. Test depuis l'application**

```bash
# Démarrer l'application
./dev-setup.sh

# Tester upload photo dans l'interface
# http://localhost:5000/choix-prestation
```

## 📋 **Configuration finale .env**

Votre `.env` devrait contenir :

```bash
# Google Cloud Storage
GOOGLE_CLOUD_PROJECT_ID=conciergerie-cordo
GCS_BUCKET_NAME=conciergerie-cordo-photos
GOOGLE_APPLICATION_CREDENTIALS=/absolute/path/to/gcs-service-account.json
```

## 🔒 **Sécurité et permissions**

### **Permissions du bucket :**
- ✅ **Lecture publique** pour les photos (URLs directes)
- ✅ **Écriture** pour le service account uniquement
- ✅ **Suppression** pour le service account (commandes annulées)

### **Service Account :**
- ✅ **Storage Admin** sur le projet
- ✅ **Clé JSON** sécurisée (ne pas commiter dans Git)

## 💰 **Coûts estimés**

Pour une cordonnerie :
- **Stockage** : ~€0.02/GB/mois (Europe)
- **Opérations** : ~€0.05/10000 requêtes
- **Trafic sortant** : €0.12/GB (vers internet)

**Estimation** : < €5/mois pour des centaines de photos

## ⚠️ **Notes importantes**

1. **ID de projet** : `conciergerie-cordo` (si pris, vous devrez choisir un autre nom)
2. **Nom de bucket** : `conciergerie-cordo-photos` (si pris, vous devrez choisir un autre nom)
3. **Facturation** : Activez la facturation dans la console Google Cloud
4. **Clé JSON** : Ne jamais commiter dans Git !
5. **Production** : Utilisez un bucket séparé pour la prod

## 🚀 **Déploiement Fly.io avec GCS**

```bash
# Upload de la clé de service sur Fly.io
fly secrets set GOOGLE_APPLICATION_CREDENTIALS="$(cat gcs-service-account.json | base64)"
fly secrets set GOOGLE_CLOUD_PROJECT_ID="conciergerie-cordo"
fly secrets set GCS_BUCKET_NAME="conciergerie-cordo-photos"
```

## 🔧 **Commandes utiles**

```bash
# Lister les buckets
gcloud storage buckets list

# Lister les fichiers dans le bucket
gcloud storage ls gs://conciergerie-cordo-photos

# Voir les permissions du bucket
gcloud storage buckets describe gs://conciergerie-cordo-photos

# Supprimer un fichier
gcloud storage rm gs://conciergerie-cordo-photos/path/to/file.jpg
```