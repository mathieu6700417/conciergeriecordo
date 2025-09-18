from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.prestations import Prestation
from models.enums import TypeChaussure
from models.commandes import Commande, StatutCommande
from services.email import email_manager
import stripe
import os

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    """Page d'accueil"""
    return render_template('home.html')

@main_bp.route('/choix-prestation')
def choix_prestation():
    """Page de commande accessible via QR code"""
    # Gérer le paramètre type pour compatibilité (si quelqu'un utilise ?type=homme/femme)
    type_param = request.args.get('type')
    if type_param:
        # Rediriger vers la page sans paramètre pour éviter les erreurs
        return redirect(url_for('main.choix_prestation'))

    # Récupérer toutes les prestations actives
    prestations_homme = Prestation.query.filter_by(
        type_chaussure=TypeChaussure.HOMME,
        actif=True
    ).all()

    prestations_femme = Prestation.query.filter_by(
        type_chaussure=TypeChaussure.FEMME,
        actif=True
    ).all()

    return render_template('choix_prestation.html',
                         prestations_homme=[p.to_dict() for p in prestations_homme],
                         prestations_femme=[p.to_dict() for p in prestations_femme])

@main_bp.route('/checkout')
def checkout():
    """Page de résultat du checkout Stripe"""
    session_id = request.args.get('session_id')

    if not session_id:
        return render_template('checkout.html', status='error',
                             error_message='Session de paiement invalide')

    try:
        # Configurer Stripe
        stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

        # Récupérer la session Stripe
        checkout_session = stripe.checkout.Session.retrieve(session_id)

        if checkout_session.payment_status == 'paid':
            # Récupérer la commande associée
            commande_id = checkout_session.metadata.get('commande_id')
            commande = Commande.query.get(commande_id)

            if commande:
                return render_template('checkout.html', status='success',
                                     commande=commande)
            else:
                return render_template('checkout.html', status='error',
                                     error_message='Commande introuvable')
        else:
            return render_template('checkout.html', status='error',
                                 error_message='Paiement non confirmé')

    except stripe.error.StripeError as e:
        return render_template('checkout.html', status='error',
                             error_message=f'Erreur Stripe: {str(e)}')
    except Exception as e:
        return render_template('checkout.html', status='error',
                             error_message='Une erreur inattendue s\'est produite')

@main_bp.route('/checkout/cancel')
def checkout_cancel():
    """Page d'annulation du checkout"""
    return render_template('checkout.html', status='cancel')

@main_bp.route('/webhook/stripe', methods=['POST'])
def stripe_webhook():
    """Webhook Stripe pour traiter les événements de paiement"""
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')

    try:
        # Configurer Stripe
        stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
        endpoint_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')

        # Vérifier la signature du webhook
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )

        # Traiter l'événement
        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            # Mettre à jour le statut de la commande
            commande_id = payment_intent.metadata.get('commande_id')
            if commande_id:
                commande = Commande.query.get(commande_id)
                if commande:
                    commande.statut = StatutCommande.PAID
                    commande.stripe_payment_intent_id = payment_intent['id']
                    from app import db
                    db.session.commit()

                    # Envoyer emails de confirmation
                    try:
                        # Email de confirmation au client
                        email_manager.send_order_confirmation(commande)

                        # Email de notification à l'admin
                        email_manager.send_admin_notification(commande)
                    except Exception as e:
                        print(f"Error sending confirmation emails: {e}")

        elif event['type'] == 'payment_intent.payment_failed':
            payment_intent = event['data']['object']
            # Traiter l'échec de paiement
            commande_id = payment_intent.metadata.get('commande_id')
            if commande_id:
                commande = Commande.query.get(commande_id)
                if commande:
                    try:
                        # Envoyer email d'échec de paiement
                        error_message = payment_intent.get('last_payment_error', {}).get('message')
                        email_manager.send_payment_failed_email(commande, error_message)
                    except Exception as e:
                        print(f"Error sending payment failed email: {e}")

        return {'status': 'success'}, 200

    except ValueError as e:
        # Payload invalide
        return {'error': 'Payload invalide'}, 400
    except stripe.error.SignatureVerificationError as e:
        # Signature invalide
        return {'error': 'Signature invalide'}, 400
    except Exception as e:
        return {'error': str(e)}, 500