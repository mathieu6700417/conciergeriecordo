# Configuration Gmail SMTP - Conciergerie Cordo

## 🔧 **Étapes de configuration**

### **1. Activer la validation en 2 étapes sur Gmail**

1. Aller sur [myaccount.google.com](https://myaccount.google.com)
2. **Sécurité** → **Connexion à Google**
3. **Validation en 2 étapes** → **Activer**
4. Suivre les instructions (SMS ou app)

### **2. Créer un mot de passe d'application**

1. Retourner dans **Sécurité** → **Validation en 2 étapes**
2. En bas, **Mots de passe des applications**
3. **Sélectionner une application** → **Autre (nom personnalisé)**
4. Nom : `Conciergerie Cordo`
5. **Générer**
6. Copier le mot de passe de 16 caractères (format: `abcd efgh ijkl mnop`)

### **3. Configurer dans .env**

Remplacer dans votre fichier `.env` :

```bash
# Email Gmail SMTP
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=votre-email@gmail.com
SMTP_PASSWORD=abcdefghijklmnop
FROM_EMAIL=votre-email@gmail.com
ADMIN_EMAIL=votre-email@gmail.com
```

**Exemple concret :**
```bash
SMTP_USER=mathieu.durand@gmail.com
SMTP_PASSWORD=abcd efgh ijkl mnop
FROM_EMAIL=mathieu.durand@gmail.com
ADMIN_EMAIL=mathieu.durand@gmail.com
```

## 📧 **Pour la production**

### **Option 1 : Utiliser votre Gmail personnel**
```bash
SMTP_USER=votre-email@gmail.com
FROM_EMAIL=votre-email@gmail.com
```

### **Option 2 : Créer un compte dédié (recommandé)**
1. Créer `contact@gmail.com` ou `conciergerie.cordo@gmail.com`
2. Activer la 2FA et créer un mot de passe d'application
3. Configurer :
```bash
SMTP_USER=conciergerie.cordo@gmail.com
FROM_EMAIL=conciergerie.cordo@gmail.com
```

### **Option 3 : Domain email + Gmail SMTP**
Si vous avez déjà `contact@conciergeriecordo.com` :
1. Configurer la redirection vers Gmail
2. Utiliser Gmail SMTP avec alias :
```bash
SMTP_USER=votre-gmail@gmail.com
FROM_EMAIL=contact@conciergeriecordo.com
```

## 🧪 **Tester la configuration**

### **1. Démarrer l'application**
```bash
./scripts/dev-setup.sh
```

### **2. Faire un test de commande**
1. Aller sur http://localhost:5000/choix-prestation
2. Ajouter une paire avec photo
3. Remplir infos client avec **votre vraie adresse email**
4. Payer avec la carte test : `4242 4242 4242 4242`
5. Vérifier la réception des emails

### **3. Configurer webhook Stripe en parallèle**
```bash
# Terminal séparé
stripe listen --forward-to localhost:5000/webhook/stripe
```

## 📋 **Checklist configuration**

- [ ] Validation 2 étapes activée sur Gmail
- [ ] Mot de passe d'application créé
- [ ] `.env` mis à jour avec vos credentials
- [ ] Application démarrée
- [ ] Webhook Stripe configuré
- [ ] Test de commande effectué
- [ ] Email de confirmation reçu

## ⚠️ **Limites Gmail SMTP**

- **500 emails/jour** en développement
- **2000 emails/jour** avec G Suite/Workspace
- Pas de problème pour une cordonnerie !

## 🔒 **Sécurité**

✅ **Bonnes pratiques :**
- Utiliser mot de passe d'application (jamais le mot de passe Gmail)
- Compte dédié pour la production
- Surveiller les connexions suspectes

❌ **À éviter :**
- Partager le mot de passe d'application
- Utiliser "Autoriser les apps moins sécurisées"
- Commiter les credentials dans Git

## 🚀 **Prêt !**

Une fois configuré, vos emails fonctionneront immédiatement. Les clients recevront :
- **Confirmation de commande** avec détails et photos
- **Récapitulatif des services** demandés
- **Informations de contact**

Et vous recevrez :
- **Notification de nouvelle commande**
- **Détails complets du client**
- **Photos des chaussures** en pièce jointe