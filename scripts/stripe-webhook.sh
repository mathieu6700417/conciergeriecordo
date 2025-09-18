#!/bin/bash

# Script pour démarrer les webhooks Stripe pour Conciergerie Cordo

echo "🎧 Démarrage des webhooks Stripe pour Conciergerie Cordo..."
echo "🌐 URL: localhost:5000/webhook/stripe"
echo ""
echo "💡 Événements écoutés:"
echo "   - payment_intent.succeeded"
echo "   - payment_intent.payment_failed"
echo ""
echo "⚠️  Gardez ce terminal ouvert pendant les tests !"
echo ""

# Vérifier que Stripe CLI est installé
if ! command -v stripe &> /dev/null; then
    echo "❌ Stripe CLI n'est pas installé"
    echo "📥 Installez-le avec: brew install stripe/stripe-cli/stripe"
    exit 1
fi

# Vérifier que le projet "conciergerie" existe
echo "🔍 Vérification du projet 'conciergerie'..."
if ! stripe config --list --project-name=conciergerie >/dev/null 2>&1; then
    echo "❌ Projet 'conciergerie' non configuré"
    echo "🔧 Créez-le avec: stripe login --project-name=conciergerie"
    echo ""
    read -p "Voulez-vous le créer maintenant ? (y/n): " create
    if [[ $create == [yY] ]]; then
        echo "🚀 Création du projet 'conciergerie'..."
        stripe login --project-name=conciergerie
    else
        exit 1
    fi
fi

# Afficher la configuration du projet
echo "📊 Configuration du projet 'conciergerie':"
stripe config --list --project-name=conciergerie | head -5
echo ""

# Démarrer l'écoute avec le projet spécifique
echo "🚀 Démarrage de l'écoute des webhooks pour Conciergerie..."
stripe listen --project-name=conciergerie --forward-to localhost:8000/webhook/stripe