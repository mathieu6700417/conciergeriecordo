import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from datetime import datetime
import requests

class EmailManager:
    def __init__(self):
        self.smtp_host = os.environ.get('SMTP_HOST')
        self.smtp_port = int(os.environ.get('SMTP_PORT', 587))
        self.smtp_user = os.environ.get('SMTP_USER')
        self.smtp_password = os.environ.get('SMTP_PASSWORD')
        self.from_email = os.environ.get('FROM_EMAIL')
        self.admin_email = os.environ.get('ADMIN_EMAIL')

    def is_configured(self):
        """Check if email is properly configured"""
        return all([
            self.smtp_host,
            self.smtp_user,
            self.smtp_password,
            self.from_email,
            self.admin_email
        ])

    def send_email(self, to_email, subject, html_content, text_content=None, attachments=None):
        """Send an email"""
        if not self.is_configured():
            print("Warning: Email not configured")
            return False

        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email

            # Add text content
            if text_content:
                text_part = MIMEText(text_content, 'plain', 'utf-8')
                msg.attach(text_part)

            # Add HTML content
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)

            # Add attachments if any
            if attachments:
                for attachment in attachments:
                    if 'data' in attachment and 'filename' in attachment:
                        img = MIMEImage(attachment['data'])
                        img.add_header('Content-Disposition', f'attachment; filename="{attachment["filename"]}"')
                        msg.attach(img)

            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            print(f"Email sent successfully to {to_email}")
            return True

        except Exception as e:
            print(f"Error sending email: {e}")
            return False

    def send_order_confirmation(self, commande):
        """Send order confirmation email to customer"""
        subject = f"Confirmation de commande #{commande.id} - Conciergerie Cordo"

        # Calculate total and generate order details
        order_details = []
        total = 0

        for i, paire in enumerate(commande.paires, 1):
            paire_total = 0
            services = []

            for paire_prestation in paire.paire_prestations:
                prestation = paire_prestation.prestation
                services.append({
                    'nom': prestation.nom,
                    'prix': float(paire_prestation.prix_unitaire)
                })
                paire_total += float(paire_prestation.prix_unitaire)

            order_details.append({
                'numero': i,
                'type': paire.type_chaussure.value.capitalize(),
                'services': services,
                'total': paire_total,
                'photo_url': paire.photo_url
            })
            total += paire_total

        # Generate HTML content
        html_content = self._generate_customer_email_html(commande, order_details, total)
        text_content = self._generate_customer_email_text(commande, order_details, total)

        return self.send_email(commande.email, subject, html_content, text_content)

    def send_admin_notification(self, commande):
        """Send new order notification to admin"""
        subject = f"NOUVELLE COMMANDE #{commande.id} - {commande.entreprise}"

        # Generate order details for admin
        order_details = []
        total = 0

        for i, paire in enumerate(commande.paires, 1):
            paire_total = 0
            services = []

            for paire_prestation in paire.paire_prestations:
                prestation = paire_prestation.prestation
                services.append({
                    'nom': prestation.nom,
                    'prix': float(paire_prestation.prix_unitaire)
                })
                paire_total += float(paire_prestation.prix_unitaire)

            order_details.append({
                'numero': i,
                'type': paire.type_chaussure.value.capitalize(),
                'services': services,
                'total': paire_total,
                'photo_url': paire.photo_url,
                'description': paire.description
            })
            total += paire_total

        # Download images for attachment (if small enough)
        attachments = []
        try:
            for paire in commande.paires:
                if paire.photo_url and paire.photo_url.startswith('http'):
                    response = requests.get(paire.photo_url, timeout=10)
                    if response.status_code == 200 and len(response.content) < 5 * 1024 * 1024:  # 5MB max
                        attachments.append({
                            'data': response.content,
                            'filename': f"paire_{paire.id}_{paire.photo_filename or 'photo.jpg'}"
                        })
        except Exception as e:
            print(f"Error downloading images for email: {e}")

        # Generate HTML content
        html_content = self._generate_admin_email_html(commande, order_details, total)
        text_content = self._generate_admin_email_text(commande, order_details, total)

        return self.send_email(self.admin_email, subject, html_content, text_content, attachments)

    def send_payment_failed_email(self, commande, error_message=None):
        """Send payment failed notification"""
        subject = f"Échec de paiement - Commande #{commande.id}"

        html_content = f"""
        <h2>Échec de paiement</h2>
        <p>Bonjour {commande.nom},</p>
        <p>Nous n'avons pas pu traiter le paiement de votre commande #{commande.id}.</p>
        {f'<p><strong>Raison :</strong> {error_message}</p>' if error_message else ''}
        <p>Vous pouvez recommencer le paiement en utilisant le lien suivant :</p>
        <p><a href="https://{os.environ.get('DOMAIN', 'localhost')}/choix-prestation">Recommencer</a></p>
        <p>Si vous avez des questions, contactez-nous à {self.from_email}</p>
        """

        text_content = f"""
        Échec de paiement

        Bonjour {commande.nom},

        Nous n'avons pas pu traiter le paiement de votre commande #{commande.id}.
        {f'Raison : {error_message}' if error_message else ''}

        Vous pouvez recommencer le paiement en visitant notre site.

        Si vous avez des questions, contactez-nous à {self.from_email}
        """

        return self.send_email(commande.email, subject, html_content, text_content)

    def _generate_customer_email_html(self, commande, order_details, total):
        """Generate HTML email content for customer"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #0d6efd; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .order-item {{ border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px; }}
                .total {{ background-color: #f8f9fa; padding: 15px; font-size: 1.2em; font-weight: bold; }}
                .footer {{ background-color: #f8f9fa; padding: 20px; text-align: center; font-size: 0.9em; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Confirmation de commande</h1>
                    <p>Commande #{commande.id}</p>
                </div>

                <div class="content">
                    <h2>Bonjour {commande.nom},</h2>
                    <p>Merci pour votre commande ! Nous avons bien reçu votre demande de service de cordonnerie.</p>

                    <h3>Détails de votre commande :</h3>
                    {''.join([f'''
                    <div class="order-item">
                        <h4>Paire {item["numero"]} - {item["type"]}</h4>
                        <ul>
                            {''.join([f'<li>{service["nom"]} - {service["prix"]:.2f} €</li>' for service in item["services"]])}
                        </ul>
                        <p><strong>Sous-total : {item["total"]:.2f} €</strong></p>
                    </div>
                    ''' for item in order_details])}

                    <div class="total">
                        Total payé : {total:.2f} €
                    </div>

                    <h3>Informations importantes :</h3>
                    <ul>
                        <li>Délai de traitement : 3-5 jours ouvrés</li>
                        <li>Livraison directement dans votre entreprise : {commande.entreprise}</li>
                    </ul>

                    <p>Pour toute question, contactez-nous :</p>
                    <ul>
                        <li>Email : {self.from_email}</li>
                        <li>Téléphone : 07 68 85 15 88</li>
                    </ul>
                </div>

                <div class="footer">
                    <p>Conciergerie Cordo - Service de cordonnerie pour entreprises</p>
                    <p>Bordeaux • Pessac • Talence • Mérignac • Bègles • Villenave d'Ornon</p>
                </div>
            </div>
        </body>
        </html>
        """

    def _generate_customer_email_text(self, commande, order_details, total):
        """Generate text email content for customer"""
        order_text = '\n'.join([
            f"Paire {item['numero']} - {item['type']}\n" +
            '\n'.join([f"  - {service['nom']} - {service['prix']:.2f} €" for service in item['services']]) +
            f"\n  Sous-total : {item['total']:.2f} €\n"
            for item in order_details
        ])

        return f"""
        Confirmation de commande #{commande.id}

        Bonjour {commande.nom},

        Merci pour votre commande ! Nous avons bien reçu votre demande de service de cordonnerie.

        Détails de votre commande :
        {order_text}

        Total payé : {total:.2f} €

        Informations importantes :
        - Délai de traitement : 3-5 jours ouvrés
        - Livraison directement dans votre entreprise : {commande.entreprise}

        Pour toute question, contactez-nous :
        - Email : {self.from_email}
        - Téléphone : 07 68 85 15 88

        Conciergerie Cordo - Service de cordonnerie pour entreprises
        Bordeaux • Pessac • Talence • Mérignac • Bègles • Villenave d'Ornon
        """

    def _generate_admin_email_html(self, commande, order_details, total):
        """Generate HTML email content for admin"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #dc3545; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .customer-info {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0; }}
                .order-item {{ border: 1px solid #ddd; margin: 15px 0; padding: 15px; border-radius: 5px; }}
                .total {{ background-color: #d4edda; padding: 15px; font-size: 1.2em; font-weight: bold; }}
                .photo {{ max-width: 200px; height: auto; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>NOUVELLE COMMANDE</h1>
                    <p>Commande #{commande.id}</p>
                </div>

                <div class="content">
                    <div class="customer-info">
                        <h3>Informations client :</h3>
                        <p><strong>Nom :</strong> {commande.nom}</p>
                        <p><strong>Email :</strong> {commande.email}</p>
                        <p><strong>Téléphone :</strong> {commande.telephone}</p>
                        <p><strong>Entreprise :</strong> {commande.entreprise}</p>
                        <p><strong>Date :</strong> {commande.created_at.strftime('%d/%m/%Y à %H:%M')}</p>
                    </div>

                    <h3>Détail des paires :</h3>
                    {''.join([f'''
                    <div class="order-item">
                        <h4>Paire {item["numero"]} - {item["type"]}</h4>
                        {f'<p><strong>Description :</strong> {item["description"]}</p>' if item.get("description") else ''}
                        <div style="display: flex; gap: 20px;">
                            <div style="flex: 1;">
                                <h5>Services demandés :</h5>
                                <ul>
                                    {''.join([f'<li>{service["nom"]} - {service["prix"]:.2f} €</li>' for service in item["services"]])}
                                </ul>
                                <p><strong>Sous-total : {item["total"]:.2f} €</strong></p>
                            </div>
                            {f'<div><img src="{item["photo_url"]}" class="photo" alt="Photo paire {item["numero"]}"></div>' if item.get("photo_url") else ''}
                        </div>
                    </div>
                    ''' for item in order_details])}

                    <div class="total">
                        Total de la commande : {total:.2f} €
                    </div>

                    <p><strong>Actions à faire :</strong></p>
                    <ol>
                        <li>Contacter le client pour organiser la récupération</li>
                        <li>Programmer la récupération des chaussures</li>
                        <li>Effectuer les réparations demandées</li>
                        <li>Livrer chez {commande.entreprise}</li>
                    </ol>
                </div>
            </div>
        </body>
        </html>
        """

    def _generate_admin_email_text(self, commande, order_details, total):
        """Generate text email content for admin"""
        order_text = '\n'.join([
            f"Paire {item['numero']} - {item['type']}\n" +
            (f"Description : {item['description']}\n" if item.get('description') else '') +
            '\n'.join([f"  - {service['nom']} - {service['prix']:.2f} €" for service in item['services']]) +
            f"\n  Sous-total : {item['total']:.2f} €\n"
            for item in order_details
        ])

        return f"""
        NOUVELLE COMMANDE #{commande.id}

        Informations client :
        - Nom : {commande.nom}
        - Email : {commande.email}
        - Téléphone : {commande.telephone}
        - Entreprise : {commande.entreprise}
        - Date : {commande.created_at.strftime('%d/%m/%Y à %H:%M')}

        Détail des paires :
        {order_text}

        Total de la commande : {total:.2f} €

        Actions à faire :
        1. Contacter le client pour organiser la récupération
        2. Programmer la récupération des chaussures
        3. Effectuer les réparations demandées
        4. Livrer chez {commande.entreprise}
        """

# Global instance
email_manager = EmailManager()