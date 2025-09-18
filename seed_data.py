#!/usr/bin/env python3
"""
Script pour initialiser la base de données avec des données de test
"""

from app import create_app, db
from models.prestations import Prestation, TypeChaussure
from decimal import Decimal

def seed_prestations():
    """Créer les prestations par défaut"""

    prestations_data = [
        # Prestations Homme
        {
            'nom': 'Patin',
            'prix': Decimal('15.00'),
            'type_chaussure': TypeChaussure.HOMME,
            'description': 'Réparation et remplacement de patins pour chaussures homme'
        },
        {
            'nom': 'Talon',
            'prix': Decimal('20.00'),
            'type_chaussure': TypeChaussure.HOMME,
            'description': 'Réparation et changement de talons pour chaussures homme'
        },
        {
            'nom': 'Patin Gomme',
            'prix': Decimal('18.00'),
            'type_chaussure': TypeChaussure.HOMME,
            'description': 'Pose de patins en gomme antidérapante pour chaussures homme'
        },
        {
            'nom': 'Talon Gomme',
            'prix': Decimal('25.00'),
            'type_chaussure': TypeChaussure.HOMME,
            'description': 'Installation de talons en gomme pour chaussures homme'
        },
        {
            'nom': 'Resemmelage complet basket',
            'prix': Decimal('45.00'),
            'type_chaussure': TypeChaussure.HOMME,
            'description': 'Resemmelage complet pour baskets et chaussures de sport homme'
        },

        # Prestations Femme
        {
            'nom': 'Patin',
            'prix': Decimal('15.00'),
            'type_chaussure': TypeChaussure.FEMME,
            'description': 'Réparation et remplacement de patins pour chaussures femme'
        },
        {
            'nom': 'Talon',
            'prix': Decimal('22.00'),
            'type_chaussure': TypeChaussure.FEMME,
            'description': 'Réparation et changement de talons pour chaussures femme'
        },
        {
            'nom': 'Patin Gomme',
            'prix': Decimal('18.00'),
            'type_chaussure': TypeChaussure.FEMME,
            'description': 'Pose de patins en gomme antidérapante pour chaussures femme'
        },
        {
            'nom': 'Talon Gomme',
            'prix': Decimal('25.00'),
            'type_chaussure': TypeChaussure.FEMME,
            'description': 'Installation de talons en gomme pour chaussures femme'
        },
        {
            'nom': 'Resemmelage complet basket',
            'prix': Decimal('42.00'),
            'type_chaussure': TypeChaussure.FEMME,
            'description': 'Resemmelage complet pour baskets et chaussures de sport femme'
        },
    ]

    for prestation_data in prestations_data:
        # Vérifier si la prestation existe déjà
        existing = Prestation.query.filter_by(
            nom=prestation_data['nom'],
            type_chaussure=prestation_data['type_chaussure']
        ).first()

        if not existing:
            prestation = Prestation(**prestation_data)
            db.session.add(prestation)
            print(f"Ajout de la prestation: {prestation.nom} - {prestation.type_chaussure.value}")
        else:
            print(f"Prestation déjà existante: {existing.nom} - {existing.type_chaussure.value}")

def main():
    """Fonction principale"""
    app = create_app()

    with app.app_context():
        print("Initialisation des données de base...")

        # Créer les tables si elles n'existent pas
        db.create_all()

        # Ajouter les prestations
        seed_prestations()

        # Sauvegarder les changements
        try:
            db.session.commit()
            print("✅ Données initialisées avec succès!")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Erreur lors de l'initialisation: {e}")

if __name__ == '__main__':
    main()