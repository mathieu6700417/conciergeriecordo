#!/bin/bash

# Script pour synchroniser les secrets Fly.io avec .env.production
# Usage: ./scripts/sync-fly-secrets.sh

set -e

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🔄 Synchronisation des secrets Fly.io avec .env.production${NC}"

# Vérifier que le fichier .env.production existe
if [ ! -f ".env.production" ]; then
    echo -e "${RED}❌ Fichier .env.production introuvable${NC}"
    exit 1
fi

# Vérifier que fly CLI est installé
if ! command -v fly &> /dev/null; then
    echo -e "${RED}❌ fly CLI n'est pas installé. Installez-le depuis https://fly.io/docs/hands-on/install-flyctl/${NC}"
    exit 1
fi

# Charger les variables depuis .env.production
echo -e "${YELLOW}📖 Lecture du fichier .env.production...${NC}"

# Fonction pour définir un secret Fly.io
set_fly_secret() {
    local key=$1
    local value=$2

    if [ -z "$value" ] || [[ "$value" == *"YOUR"* ]] || [[ "$value" == *"your"* ]] || [[ "$value" == "..." ]]; then
        echo -e "${YELLOW}⚠️  $key n'est pas configuré ou contient une valeur par défaut, ignoré${NC}"
        return
    fi

    echo -e "${GREEN}✅ Configuration de $key${NC}"
    fly secrets set "$key=$value" --stage
}

# Lire et traiter chaque ligne du fichier .env.production
secrets_count=0
while IFS= read -r line; do
    # Ignorer les commentaires et lignes vides
    if [[ "$line" =~ ^#.*$ ]] || [ -z "$line" ]; then
        continue
    fi

    # Extraire la clé et la valeur
    if [[ "$line" =~ ^([^=]+)=(.*)$ ]]; then
        key="${BASH_REMATCH[1]}"
        value="${BASH_REMATCH[2]}"

        # Retirer les guillemets si présents
        value="${value%\"}"
        value="${value#\"}"

        # Définir le secret
        set_fly_secret "$key" "$value"
        ((secrets_count++))
    fi
done < .env.production

# Déployer les secrets
if [ $secrets_count -gt 0 ]; then
    echo -e "${GREEN}🚀 Déploiement des $secrets_count secrets...${NC}"
    fly secrets deploy
    echo -e "${GREEN}✅ Synchronisation terminée avec succès!${NC}"
    echo -e "${YELLOW}💡 Les secrets ont été configurés mais l'application doit être redéployée pour les prendre en compte${NC}"
    echo -e "${YELLOW}   Utilisez: fly deploy${NC}"
else
    echo -e "${YELLOW}⚠️  Aucun secret valide trouvé dans .env.production${NC}"
    echo -e "${YELLOW}   Assurez-vous de configurer vos vraies valeurs dans .env.production${NC}"
fi

# Afficher les secrets configurés (sans les valeurs)
echo -e "\n${GREEN}📋 Secrets actuellement configurés sur Fly.io:${NC}"
fly secrets list