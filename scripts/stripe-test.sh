#!/bin/bash

# Script pour tester les paiements Stripe avec le profil Conciergerie

echo "🧪 Tests Stripe pour Conciergerie Cordo"
echo "📝 Profil: conciergerie"
echo ""

# Vérifier que le projet existe
if ! stripe config --list --project-name=conciergerie >/dev/null 2>&1; then
    echo "❌ Projet 'conciergerie' non trouvé"
    echo "🔧 Créez-le avec: stripe login --project-name=conciergerie"
    exit 1
fi

echo "💳 Tests de paiement disponibles:"
echo ""
echo "1️⃣  Paiement réussi"
echo "   stripe trigger payment_intent.succeeded --project-name=conciergerie"
echo ""
echo "2️⃣  Paiement échoué"
echo "   stripe trigger payment_intent.payment_failed --project-name=conciergerie"
echo ""
echo "3️⃣  Voir les événements récents"
echo "   stripe events list --project-name=conciergerie --limit 5"
echo ""

# Menu interactif
echo "Choisissez un test (1, 2, 3) ou 'q' pour quitter:"
read -r choice

case $choice in
    1)
        echo "🚀 Déclenchement d'un paiement réussi..."
        stripe trigger payment_intent.succeeded --project-name=conciergerie
        ;;
    2)
        echo "🚀 Déclenchement d'un paiement échoué..."
        stripe trigger payment_intent.payment_failed --project-name=conciergerie
        ;;
    3)
        echo "📋 Événements récents:"
        stripe events list --project-name=conciergerie --limit 5
        ;;
    q|Q)
        echo "👋 Au revoir !"
        exit 0
        ;;
    *)
        echo "❌ Choix invalide"
        exit 1
        ;;
esac