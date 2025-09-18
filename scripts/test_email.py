#!/usr/bin/env python3
"""
Script pour tester la configuration email
"""

import os
from dotenv import load_dotenv
from services.email import email_manager

# Charger les variables d'environnement
load_dotenv()

def test_email_config():
    """Tester la configuration email"""
    print("🧪 Test de la configuration email...")
    print(f"SMTP Host: {os.getenv('SMTP_HOST')}")
    print(f"SMTP Port: {os.getenv('SMTP_PORT')}")
    print(f"SMTP User: {os.getenv('SMTP_USER')}")
    print(f"From Email: {os.getenv('FROM_EMAIL')}")
    print(f"Admin Email: {os.getenv('ADMIN_EMAIL')}")
    print()

    if not email_manager.is_configured():
        print("❌ Configuration email incomplète !")
        print("Vérifiez les variables d'environnement suivantes :")
        print("- SMTP_HOST")
        print("- SMTP_USER")
        print("- SMTP_PASSWORD")
        print("- FROM_EMAIL")
        print("- ADMIN_EMAIL")
        return False

    print("✅ Configuration email complète !")
    return True

def send_test_email():
    """Envoyer un email de test"""
    if not test_email_config():
        return

    # Demander l'email de destination
    to_email = input("📧 Entrez votre email pour le test : ").strip()
    if not to_email:
        print("❌ Email requis !")
        return

    # Email de test
    subject = "🧪 Test Conciergerie Cordo"
    html_content = """
    <h2>Test de configuration email</h2>
    <p>Si vous recevez cet email, la configuration Gmail SMTP fonctionne parfaitement ! 🎉</p>
    <p><strong>Conciergerie Cordo</strong><br>
    Service de cordonnerie pour entreprises</p>
    """

    text_content = """
    Test de configuration email

    Si vous recevez cet email, la configuration Gmail SMTP fonctionne parfaitement !

    Conciergerie Cordo
    Service de cordonnerie pour entreprises
    """

    print(f"📤 Envoi de l'email de test vers {to_email}...")

    success = email_manager.send_email(
        to_email=to_email,
        subject=subject,
        html_content=html_content,
        text_content=text_content
    )

    if success:
        print("✅ Email envoyé avec succès !")
        print("📫 Vérifiez votre boîte de réception (et spams)")
    else:
        print("❌ Échec de l'envoi email")
        print("💡 Vérifiez :")
        print("  - Mot de passe d'application Gmail correct")
        print("  - Validation en 2 étapes activée")
        print("  - Connexion internet")

if __name__ == '__main__':
    send_test_email()