#!/bin/bash

# Script automatique pour configurer Google Cloud Storage
# pour Conciergerie Cordo

set -e

echo "🚀 Configuration Google Cloud Storage pour Conciergerie Cordo"
echo ""

# Vérifier si gcloud est installé
if ! command -v gcloud &> /dev/null; then
    echo "❌ Google Cloud CLI n'est pas installé."
    echo "📥 Installez-le avec: brew install google-cloud-sdk"
    echo "📖 Ou suivez: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Noms fixes pour le projet et bucket
PROJECT_ID="conciergerie-cordo"
BUCKET_NAME="conciergerie-cordo-photos"
SERVICE_ACCOUNT_NAME="conciergerie-cordo-storage"

echo "📝 Configuration:"
echo "   Projet: $PROJECT_ID"
echo "   Bucket: $BUCKET_NAME"
echo "   Service Account: $SERVICE_ACCOUNT_NAME"
echo ""

# Authentification
echo "🔐 Vérification de l'authentification..."
if ! gcloud auth list --filter="status:ACTIVE" --format="value(account)" | grep -q "."; then
    echo "🔑 Authentification requise..."
    gcloud auth login
fi

# Vérifier si le projet existe déjà
echo "🔍 Vérification de l'existence du projet $PROJECT_ID..."
if gcloud projects describe $PROJECT_ID >/dev/null 2>&1; then
    echo "✅ Projet $PROJECT_ID trouvé, utilisation du projet existant"
    gcloud config set project $PROJECT_ID
else
    echo "📁 Création du projet $PROJECT_ID..."
    if gcloud projects create $PROJECT_ID --name="Conciergerie Cordo" --set-as-default; then
        echo "✅ Projet créé avec succès"
    else
        echo "❌ Impossible de créer le projet $PROJECT_ID"
        echo "💡 Raisons possibles :"
        echo "   - L'ID est déjà pris par un autre utilisateur"
        echo "   - Permissions insuffisantes"
        echo "   - Quota de projets atteint"
        echo ""
        echo "🔧 Solutions :"
        echo "   - Modifiez PROJECT_ID dans le script avec un nom unique"
        echo "   - Utilisez un projet existant en modifiant le script"
        exit 1
    fi
fi

# Vérifier la facturation
echo "💳 Vérification de la facturation..."
BILLING_ENABLED=$(gcloud beta billing projects describe $PROJECT_ID --format="value(billingEnabled)" 2>/dev/null || echo "false")
if [ "$BILLING_ENABLED" != "true" ]; then
    echo "⚠️  La facturation n'est pas activée pour ce projet"
    echo "💡 Activez la facturation :"
    echo "   1. Allez sur https://console.cloud.google.com/billing"
    echo "   2. Sélectionnez ou créez un compte de facturation"
    echo "   3. Liez-le au projet $PROJECT_ID"
    echo ""
    read -p "Appuyez sur Entrée une fois la facturation activée..."
fi

# Activer les APIs
echo "🔌 Activation des APIs..."
gcloud services enable storage.googleapis.com iam.googleapis.com

# Vérifier si le bucket existe déjà
echo "🔍 Vérification de l'existence du bucket $BUCKET_NAME..."
if gcloud storage buckets describe gs://$BUCKET_NAME >/dev/null 2>&1; then
    echo "✅ Bucket gs://$BUCKET_NAME trouvé, utilisation du bucket existant"
else
    echo "🪣 Création du bucket $BUCKET_NAME..."
    if gcloud storage buckets create gs://$BUCKET_NAME \
        --location=europe-west1 \
        --default-storage-class=STANDARD \
        --uniform-bucket-level-access; then
        echo "✅ Bucket créé avec succès"
    else
        echo "❌ Impossible de créer le bucket gs://$BUCKET_NAME"
        echo "💡 Raisons possibles :"
        echo "   - Le nom est déjà pris par un autre utilisateur"
        echo "   - Facturation non activée"
        echo "   - Permissions insuffisantes"
        echo ""
        echo "🔧 Solutions :"
        echo "   - Modifiez BUCKET_NAME dans le script avec un nom unique"
        echo "   - Vérifiez que la facturation est activée"
        exit 1
    fi
fi

# Configurer les permissions publiques
echo "🔓 Configuration des permissions publiques..."
gcloud storage buckets add-iam-policy-binding gs://$BUCKET_NAME \
    --member=allUsers \
    --role=roles/storage.objectViewer

# Vérifier si le service account existe déjà
echo "🔍 Vérification de l'existence du service account..."
SERVICE_ACCOUNT_EMAIL="$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com"
if gcloud iam service-accounts describe $SERVICE_ACCOUNT_EMAIL >/dev/null 2>&1; then
    echo "✅ Service account $SERVICE_ACCOUNT_EMAIL trouvé, utilisation du compte existant"
else
    echo "🤖 Création du service account..."
    if gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME \
        --display-name="Conciergerie Cordo Storage Service" \
        --description="Service account for Conciergerie Cordo photo storage"; then
        echo "✅ Service account créé"
    else
        echo "❌ Impossible de créer le service account"
        exit 1
    fi
fi

# Attribuer les permissions
echo "🔑 Attribution des permissions..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
    --role="roles/storage.admin"

# Créer la clé JSON
echo "🗝️  Création de la clé de service..."
KEY_FILE="./gcs-service-account.json"

# Supprimer l'ancienne clé s'il y en a une
if [ -f "$KEY_FILE" ]; then
    echo "🗑️  Suppression de l'ancienne clé..."
    rm -f "$KEY_FILE"
fi

if gcloud iam service-accounts keys create $KEY_FILE \
    --iam-account=$SERVICE_ACCOUNT_EMAIL; then
    echo "✅ Clé JSON créée avec succès"
else
    echo "❌ Impossible de créer la clé JSON"
    exit 1
fi

# Mettre à jour .env
echo "📝 Mise à jour du fichier .env..."
if [ -f .env ]; then
    # Supprimer les anciennes lignes GCS s'elles existent
    sed -i.bak '/^GOOGLE_CLOUD_PROJECT_ID=/d' .env
    sed -i.bak '/^GCS_BUCKET_NAME=/d' .env
    sed -i.bak '/^GOOGLE_APPLICATION_CREDENTIALS=/d' .env
    rm -f .env.bak
fi

# Ajouter les nouvelles configurations
cat >> .env << EOF

# Google Cloud Storage (mis à jour automatiquement)
GOOGLE_CLOUD_PROJECT_ID=$PROJECT_ID
GCS_BUCKET_NAME=$BUCKET_NAME
GOOGLE_APPLICATION_CREDENTIALS=$(pwd)/$KEY_FILE
EOF

echo ""
echo "✅ Configuration Google Cloud Storage terminée !"
echo ""
echo "📋 Résumé:"
echo "   ✅ Projet: $PROJECT_ID"
echo "   ✅ Bucket: gs://$BUCKET_NAME"
echo "   ✅ Service Account: $SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com"
echo "   ✅ Clé JSON: $KEY_FILE"
echo "   ✅ Fichier .env mis à jour"
echo ""
echo "🧪 Pour tester:"
echo "   python test_gcs.py"
echo ""
echo "🚀 Pour démarrer l'application:"
echo "   ./dev-setup.sh"
echo ""
echo "⚠️  IMPORTANT:"
echo "   - Ne commitez jamais le fichier $KEY_FILE dans Git"
echo "   - Activez la facturation sur https://console.cloud.google.com/billing"
echo "   - Le bucket est configuré en lecture publique pour les photos"