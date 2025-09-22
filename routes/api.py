from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from models.prestations import Prestation
from models.enums import TypeChaussure
from models.commandes import Commande, StatutCommande
from models.paires import Paire, PairePrestation
from services.storage import gcs_manager
from services.email import email_manager
from database import db
import stripe
import os
import uuid
from PIL import Image
import io
import base64

api_bp = Blueprint('api', __name__)

@api_bp.route('/prestations', methods=['GET'])
def get_prestations():
    """Récupérer toutes les prestations actives"""
    try:
        prestations = Prestation.query.filter_by(actif=True).all()
        return jsonify({
            'success': True,
            'prestations': [p.to_dict() for p in prestations]
        })
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f'Erreur dans get_prestations: {str(e)}')
        return jsonify({'success': False, 'error': 'Erreur serveur'}), 500

@api_bp.route('/prestations/<type_chaussure>', methods=['GET'])
def get_prestations_by_type(type_chaussure):
    """Récupérer les prestations par type de chaussure"""
    try:
        # Convertir le paramètre en enum (case insensitive)
        type_normalized = type_chaussure.upper()
        if type_normalized == 'HOMME':
            type_enum = TypeChaussure.HOMME
        elif type_normalized == 'FEMME':
            type_enum = TypeChaussure.FEMME
        else:
            return jsonify({'success': False, 'error': 'Type de chaussure invalide'}), 400

        prestations = Prestation.query.filter_by(
            type_chaussure=type_enum,
            actif=True
        ).all()

        return jsonify({
            'success': True,
            'prestations': [p.to_dict() for p in prestations]
        })
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f'Erreur dans get_prestations_by_type: {str(e)}')
        return jsonify({'success': False, 'error': 'Erreur serveur'}), 500

@api_bp.route('/upload-photo', methods=['POST'])
def upload_photo():
    """Upload d'une photo pour une paire de chaussures"""
    try:
        # Récupérer les données de la photo (base64)
        if not request.json:
            current_app.logger.error('No JSON data in upload request')
            return jsonify({'success': False, 'error': 'Aucune donnée JSON fournie'}), 400

        photo_data = request.json.get('photo')
        if not photo_data:
            current_app.logger.error('No photo data provided')
            return jsonify({'success': False, 'error': 'Aucune photo fournie'}), 400

        # Décoder la photo base64
        try:
            # Retirer le préfixe data:image/...;base64,
            if 'base64,' in photo_data:
                photo_data = photo_data.split('base64,')[1]

            image_data = base64.b64decode(photo_data)
            image = Image.open(io.BytesIO(image_data))

            # Redimensionner l'image si nécessaire
            max_size = (1024, 1024)
            if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
                image.thumbnail(max_size, Image.Resampling.LANCZOS)

            # Convertir en JPEG
            if image.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background

            # Upload vers Google Cloud Storage (obligatoire)
            if not gcs_manager.is_configured():
                current_app.logger.error('GCS not configured')
                return jsonify({
                    'success': False,
                    'error': 'Google Cloud Storage non configuré. Veuillez configurer GCS.'
                }), 500

            try:
                # Convert image to bytes
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format='JPEG', quality=85, optimize=True)
                img_byte_arr.seek(0)

                # For temporary upload, use a temporary ID
                temp_id = str(uuid.uuid4())
                result = gcs_manager.upload_image(
                    img_byte_arr.getvalue(),
                    temp_id,
                    temp_id
                )

                return jsonify({
                    'success': True,
                    'photo_url': result['public_url'],
                    'filename': result['filename'],
                    'temp_id': temp_id
                })

            except Exception as gcs_error:
                current_app.logger.error(f'GCS upload error: {str(gcs_error)}')
                return jsonify({
                    'success': False,
                    'error': f'Erreur lors de l\'upload vers Google Cloud Storage: {str(gcs_error)}'
                }), 500

        except Exception as e:
            current_app.logger.error(f'Image processing error: {str(e)}')
            return jsonify({'success': False, 'error': f'Erreur de traitement de l\'image: {str(e)}'}), 400

    except IOError as e:
        current_app.logger.error(f'File IO error: {str(e)}')
        return jsonify({'success': False, 'error': f'Erreur de fichier: {str(e)}'}), 400
    except Exception as e:
        current_app.logger.error(f'Unexpected error in upload_photo: {str(e)}')
        return jsonify({'success': False, 'error': 'Erreur serveur'}), 500

@api_bp.route('/commande', methods=['POST'])
def create_commande():
    """Créer une nouvelle commande"""
    try:
        data = request.json

        # Validation des données
        required_fields = ['nom', 'email', 'telephone', 'entreprise', 'paires']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'success': False, 'error': f'Champ requis manquant: {field}'}), 400

        if not data['paires'] or len(data['paires']) == 0:
            return jsonify({'success': False, 'error': 'Au moins une paire de chaussures est requise'}), 400

        # Créer la commande
        commande = Commande(
            nom=data['nom'],
            email=data['email'],
            telephone=data['telephone'],
            entreprise=data['entreprise'],
            statut=StatutCommande.PENDING,
            total=0  # Sera calculé plus tard
        )

        db.session.add(commande)
        db.session.flush()  # Pour obtenir l'ID de la commande

        total_commande = 0

        # Créer les paires et leurs prestations
        for i, paire_data in enumerate(data['paires']):
            # Validation des données de la paire
            if 'type_chaussure' not in paire_data or 'prestations' not in paire_data:
                return jsonify({'success': False, 'error': f'Données manquantes pour la paire {i+1}'}), 400

            if not paire_data['prestations']:
                return jsonify({'success': False, 'error': f'Aucune prestation sélectionnée pour la paire {i+1}'}), 400

            # Convertir la string en enum
            type_chaussure_str = paire_data['type_chaussure']
            if type_chaussure_str == 'HOMME':
                type_chaussure_enum = TypeChaussure.HOMME
            elif type_chaussure_str == 'FEMME':
                type_chaussure_enum = TypeChaussure.FEMME
            else:
                return jsonify({'success': False, 'error': f'Type de chaussure invalide: {type_chaussure_str}'}), 400

            paire = Paire(
                commande_id=commande.id,
                type_chaussure=type_chaussure_enum,
                photo_url=paire_data.get('photo_url'),
                photo_gcs_path=paire_data.get('gcs_path'),
                photo_filename=paire_data.get('photo_filename'),
                description=paire_data.get('description'),
                ordre=i + 1
            )

            db.session.add(paire)
            db.session.flush()  # Pour obtenir l'ID de la paire

            # Ajouter les prestations pour cette paire
            for prestation_id in paire_data['prestations']:
                prestation = Prestation.query.get(prestation_id)
                if not prestation or not prestation.actif:
                    return jsonify({'success': False, 'error': f'Prestation invalide: {prestation_id}'}), 400

                # Vérifier que le type de chaussure correspond
                if prestation.type_chaussure != type_chaussure_enum:
                    return jsonify({'success': False, 'error': f'Type de chaussure incompatible pour la prestation {prestation_id}'}), 400

                paire_prestation = PairePrestation(
                    paire_id=paire.id,
                    prestation_id=prestation.id,
                    prix_unitaire=prestation.prix
                )

                db.session.add(paire_prestation)
                total_commande += float(prestation.prix)

        # Mettre à jour le total de la commande
        commande.total = total_commande

        db.session.commit()

        return jsonify({
            'success': True,
            'commande': commande.to_dict()
        })

    except ValueError as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Erreur dans save_prestations: {str(e)}')
        return jsonify({'success': False, 'error': 'Erreur serveur'}), 500

@api_bp.route('/commande/<int:commande_id>/checkout', methods=['POST'])
def create_checkout_session(commande_id):
    """Créer une session de paiement Stripe"""
    try:
        commande = Commande.query.get(commande_id)
        if not commande:
            return jsonify({'success': False, 'error': 'Commande introuvable'}), 404

        if commande.statut != StatutCommande.PENDING:
            return jsonify({'success': False, 'error': 'Commande déjà traitée'}), 400

        # Configurer Stripe
        stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

        # Créer les line items pour Stripe
        line_items = []
        for paire in commande.paires:
            for paire_prestation in paire.paire_prestations:
                prestation = paire_prestation.prestation
                line_items.append({
                    'price_data': {
                        'currency': 'eur',
                        'product_data': {
                            'name': f"{prestation.nom} - {paire.type_chaussure.value.title()}",
                            'description': prestation.description or f"Service de cordonnerie - {prestation.nom}",
                        },
                        'unit_amount': int(float(paire_prestation.prix_unitaire) * 100),  # Prix en centimes
                    },
                    'quantity': 1,
                })

        # Créer la session Stripe Checkout
        domain = request.host_url.rstrip('/')
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=f"{domain}/checkout?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{domain}/checkout/cancel",
            metadata={
                'commande_id': str(commande.id)
            },
            customer_email=commande.email,
            billing_address_collection='required',
        )

        return jsonify({
            'success': True,
            'checkout_url': checkout_session.url,
            'session_id': checkout_session.id
        })

    except stripe.error.CardError as e:
        return jsonify({'success': False, 'error': f'Carte refusée: {e.user_message}'}), 400
    except stripe.error.InvalidRequestError as e:
        return jsonify({'success': False, 'error': f'Requête invalide: {str(e)}'}), 400
    except stripe.error.StripeError as e:
        current_app.logger.error(f'Erreur Stripe dans create_checkout_session: {str(e)}')
        return jsonify({'success': False, 'error': 'Erreur de paiement'}), 500
    except Exception as e:
        current_app.logger.error(f'Erreur dans create_checkout_session: {str(e)}')
        return jsonify({'success': False, 'error': 'Erreur serveur'}), 500

@api_bp.route('/commande/<int:commande_id>', methods=['GET'])
def get_commande(commande_id):
    """Récupérer une commande par son ID"""
    try:
        commande = Commande.query.get(commande_id)
        if not commande:
            return jsonify({'success': False, 'error': 'Commande introuvable'}), 404

        return jsonify({
            'success': True,
            'commande': commande.to_dict()
        })

    except Exception as e:
        current_app.logger.error(f'Erreur dans get_commande: {str(e)}')
        return jsonify({'success': False, 'error': 'Erreur serveur'}), 500