# Configuration Webhooks Stripe

## 🔧 Développement (Test)

### 1. Utiliser Stripe CLI pour les tests locaux

```bash
# Installer Stripe CLI
# macOS
brew install stripe/stripe-cli/stripe

# Linux/Windows - voir https://stripe.com/docs/stripe-cli

# Se connecter
stripe login

# Écouter les webhooks en local
stripe listen --forward-to localhost:5000/webhook/stripe
```

La commande `stripe listen` vous donnera un webhook secret comme :
```
whsec_1234567890abcdef...
```

Mettez ce secret dans votre `.env` :
```bash
STRIPE_WEBHOOK_SECRET=whsec_1234567890abcdef...
```

### 2. Tester les paiements en local

1. Démarrer l'application : `docker-compose up`
2. Dans un autre terminal : `stripe listen --forward-to localhost:5000/webhook/stripe`
3. Aller sur http://localhost:5000/choix-prestation
4. Créer une commande avec les cartes de test Stripe :
   - **Succès** : `4242 4242 4242 4242`
   - **Échec** : `4000 0000 0000 0002`
   - Date : n'importe quelle date future
   - CVC : n'importe quel 3 chiffres

## 🚀 Production

### 1. Créer un webhook dans le dashboard Stripe

1. Aller sur https://dashboard.stripe.com/webhooks (mode Live)
2. Cliquer "Add endpoint"
3. **Endpoint URL** : `https://conciergeriecordo.com/webhook/stripe`
4. **Événements à sélectionner** :
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
5. Sauvegarder et récupérer la "Signing secret"

### 2. Configurer le secret sur Fly.io

```bash
fly secrets set STRIPE_WEBHOOK_SECRET="whsec_votre_secret_production"
```

## 🧪 Test des webhooks

### Cartes de test Stripe

| Numéro de carte | Description |
|---|---|
| `4242 4242 4242 4242` | Visa - Paiement réussi |
| `4000 0000 0000 0002` | Visa - Paiement refusé |
| `4000 0000 0000 9995` | Visa - Fonds insuffisants |
| `4000 0000 0000 9987` | Visa - Code postal invalide |

### Événements à tester

1. **Paiement réussi** :
   - Utiliser `4242 4242 4242 4242`
   - Vérifier que la commande passe en statut "paid"
   - Vérifier les emails de confirmation

2. **Paiement échoué** :
   - Utiliser `4000 0000 0000 0002`
   - Vérifier l'email d'échec de paiement

## 🔍 Debug des webhooks

### Logs Stripe CLI (développement)
```bash
stripe listen --forward-to localhost:5000/webhook/stripe --log-level debug
```

### Logs Fly.io (production)
```bash
fly logs --app conciergerie-cordo
```

### Dashboard Stripe
- Aller dans "Developers" > "Webhooks"
- Cliquer sur votre webhook
- Voir l'onglet "Recent deliveries" pour les tentatives

## ⚠️ Problèmes courants

1. **Webhook secret incorrect** : Vérifier que le secret est bien configuré
2. **URL non accessible** : Vérifier que l'application est déployée et accessible
3. **Événements manqués** : Stripe retente automatiquement pendant 3 jours
4. **HTTPS requis** : Les webhooks production nécessitent HTTPS