#!/usr/bin/env python3
"""
Script pour tester la configuration Google Cloud Storage
"""

import os
from dotenv import load_dotenv
from services.storage import gcs_manager
from PIL import Image
import io

# Charger les variables d'environnement
load_dotenv()

def test_gcs_config():
    """Tester la configuration GCS"""
    print("🧪 Test de la configuration Google Cloud Storage...")
    print(f"Project ID: {os.getenv('GOOGLE_CLOUD_PROJECT_ID')}")
    print(f"Bucket Name: {os.getenv('GCS_BUCKET_NAME')}")
    print(f"Credentials: {os.getenv('GOOGLE_APPLICATION_CREDENTIALS')}")
    print()

    if not gcs_manager.is_configured():
        print("❌ Configuration GCS incomplète !")
        print("Vérifiez les variables d'environnement suivantes :")
        print("- GOOGLE_CLOUD_PROJECT_ID")
        print("- GCS_BUCKET_NAME")
        print("- GOOGLE_APPLICATION_CREDENTIALS")
        print()
        print("💡 Lancez le script de configuration :")
        print("   ./setup-gcs.sh")
        return False

    print("✅ Configuration GCS complète !")
    return True

def create_test_image():
    """Créer une image de test"""
    # Créer une image simple de test
    img = Image.new('RGB', (200, 100), color='lightblue')

    # Convertir en bytes
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG', quality=85)
    img_byte_arr.seek(0)

    return img_byte_arr.getvalue()

def test_gcs_upload():
    """Tester l'upload vers GCS"""
    if not test_gcs_config():
        return

    try:
        print("📸 Création d'une image de test...")
        test_image_data = create_test_image()

        print("☁️  Upload vers Google Cloud Storage...")
        result = gcs_manager.upload_image(
            image_data=test_image_data,
            commande_id="test-commande",
            paire_id="test-paire",
            original_filename="test-photo.jpg"
        )

        print("✅ Upload réussi !")
        print(f"   📁 Chemin GCS: {result['gcs_path']}")
        print(f"   🌐 URL publique: {result['public_url']}")
        print(f"   📝 Nom fichier: {result['filename']}")
        print()

        # Tester l'URL signée
        print("🔐 Test de génération d'URL signée...")
        signed_url = gcs_manager.get_signed_url(result['gcs_path'], expiration_minutes=5)
        if signed_url:
            print(f"✅ URL signée générée: {signed_url[:50]}...")
        else:
            print("⚠️  Impossible de générer l'URL signée")

        # Nettoyer
        print("🧹 Nettoyage du fichier de test...")
        if gcs_manager.delete_image(result['gcs_path']):
            print("✅ Fichier de test supprimé")
        else:
            print("⚠️  Erreur lors de la suppression")

        print()
        print("🎉 Test Google Cloud Storage réussi !")
        print("📝 L'application peut maintenant stocker les photos dans le cloud")

    except Exception as e:
        print(f"❌ Erreur lors du test GCS: {e}")
        print()
        print("💡 Vérifiez :")
        print("  - La facturation est activée sur Google Cloud")
        print("  - Le fichier de credentials existe et est valide")
        print("  - Les permissions du service account")
        print("  - La connectivité internet")

def test_error_handling():
    """Tester la gestion d'erreur quand GCS n'est pas configuré"""
    print("🧪 Test de gestion d'erreur sans GCS...")

    # Temporairement désactiver GCS
    original_project = os.environ.get('GOOGLE_CLOUD_PROJECT_ID')
    if original_project:
        os.environ['GOOGLE_CLOUD_PROJECT_ID'] = ''

    try:
        # Recréer le manager sans config
        from services.storage import GCSManager
        temp_manager = GCSManager()

        if not temp_manager.is_configured():
            print("✅ Détection correcte de GCS non configuré")
        else:
            print("⚠️  GCS toujours configuré malgré la désactivation")

    finally:
        # Restaurer la configuration
        if original_project:
            os.environ['GOOGLE_CLOUD_PROJECT_ID'] = original_project

if __name__ == '__main__':
    print("🚀 Test complet de Google Cloud Storage")
    print("=" * 50)
    print()

    # Test principal
    test_gcs_upload()

    print()
    print("=" * 50)

    # Test gestion d'erreur
    test_error_handling()

    print()
    print("✅ Tests terminés !")