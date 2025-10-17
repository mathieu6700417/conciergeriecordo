#!/usr/bin/env python3
"""
Script pour initialiser la base de données avec des données de test
"""

from app import create_app, db
from models.prestations import Prestation, TypeChaussure
from decimal import Decimal

def seed_prestations():
    """Créer les prestations par défaut et désactiver les autres"""

    # Désactiver toutes les prestations existantes
    print("Désactivation de toutes les prestations existantes...")
    existing_prestations = Prestation.query.all()
    for prestation in existing_prestations:
        prestation.actif = False
        print(f"Désactivation: {prestation.nom} - {prestation.type_chaussure.value}")

    prestations_data = [
        # Prestations Homme (actives seulement)
        {
            'nom': 'Talon classique',
            'prix': Decimal('22.00'),
            'type_chaussure': TypeChaussure.HOMME,
            'description': 'Changement du talon sur une chaussure de ville homme',
            'image_filename': 'talon-homme.png',
            'actif': True
        },
        {
            'nom': 'Talon gomme',
            'prix': Decimal('25.00'),
            'type_chaussure': TypeChaussure.HOMME,
            'description': 'Réparation et remplacement de la partie talon sur une chaussure de type basket pour compenser l\'usure de la chaussure.',
            'image_filename': 'talon-gomme.png',
            'actif': True
        },
        {
            'nom': 'Patin classique',
            'prix': Decimal('26.00'),
            'type_chaussure': TypeChaussure.HOMME,
            'description': 'Pose d\'une semelle en caoutchouc antidérapante pour protéger et remédier à l\'usure naturelle d\'une chaussure. Pour chaussures de ville fines ou semelles cuir.',
            'image_filename': 'talon-patin-classique-homme.png',
            'actif': True
        },
        {
            'nom': 'Patin gomme',
            'prix': Decimal('30.00'),
            'type_chaussure': TypeChaussure.HOMME,
            'description': 'Pose d\'une semelle en caoutchouc type gomme avec du relief sur la semelle existante qui est au contact du sol pour protéger la semelle des intempéries et tenir un rôle antidérapant, ou remédier à l\'usure naturelle d\'une chaussure',
            'image_filename': 'patin-gomme.png',
            'actif': True
        },
        {
            'nom': 'Ressemelage complet Basket',
            'prix': Decimal('60.00'),
            'type_chaussure': TypeChaussure.HOMME,
            'description': 'Ressemelage complet sur une paire de basket grâce à une couche de caoutchouc avec des reliefs antidérapants. Utile pour remédier à l\'usure importante de la paire.',
            'image_filename': 'ressemelage-basket.png',
            'actif': True
        },
        {
            'nom': 'Autre (collage, couture, ...)',
            'prix': Decimal('0.00'),
            'type_chaussure': TypeChaussure.HOMME,
            'description': 'Autres réparations sur devis',
            'image_filename': None,
            'actif': True
        },

        # Prestations Femme (actives seulement)
        {
            'nom': 'Talon aiguille',
            'prix': Decimal('12.00'),
            'type_chaussure': TypeChaussure.FEMME,
            'description': 'Changement des talons aiguilles sur une paire femme (ne comprend pas la remise en beauté de l\'enrobage du talon s\'il est très abimé - nous consulter.)',
            'image_filename': 'talon-patin-classique-femme.png',
            'actif': True
        },
        {
            'nom': 'Talon classique',
            'prix': Decimal('15.00'),
            'type_chaussure': TypeChaussure.FEMME,
            'description': 'Remplacement du talon usé qui est au contact du sol.',
            'image_filename': 'talon-femme.png',
            'actif': True
        },
        {
            'nom': 'Talon gomme',
            'prix': Decimal('23.00'),
            'type_chaussure': TypeChaussure.FEMME,
            'description': 'Réparation et remplacement de la partie talon sur une chaussure de type basket pour compenser l\'usure de la chaussure.',
            'image_filename': 'talon-gomme.png',
            'actif': True
        },
        {
            'nom': 'Patin',
            'prix': Decimal('22.00'),
            'type_chaussure': TypeChaussure.FEMME,
            'description': 'Pose d\'une semelle en caoutchouc antidérapante pour protéger et remédier à l\'usure naturelle d\'une chaussure. Pour chaussures de ville fines ou semelles cuir.',
            'image_filename': 'talon-patin-classique-femme.png',
            'actif': True
        },
        {
            'nom': 'Patin gomme',
            'prix': Decimal('26.00'),
            'type_chaussure': TypeChaussure.FEMME,
            'description': 'Pose d\'une semelle en caoutchouc type gomme avec du relief sur la semelle existante qui est au contact du sol pour protéger la semelle des intempéries et tenir un rôle antidérapant, ou remédier à l\'usure naturelle d\'une chaussure',
            'image_filename': 'patin-gomme.png',
            'actif': True
        },
        {
            'nom': 'Ressemelage complet Basket',
            'prix': Decimal('50.00'),
            'type_chaussure': TypeChaussure.FEMME,
            'description': 'Ressemelage complet sur une paire de basket grâce à une couche de caoutchouc avec des reliefs antidérapants. Utile pour remédier à l\'usure importante de la paire.',
            'image_filename': 'ressemelage-basket.png',
            'actif': True
        },
        {
            'nom': 'Autre (collage, couture, ...)',
            'prix': Decimal('0.00'),
            'type_chaussure': TypeChaussure.FEMME,
            'description': 'Autres réparations sur devis',
            'image_filename': None,
            'actif': True
        },
    ]

    print("\nCréation/mise à jour des prestations actives...")
    for prestation_data in prestations_data:
        # Vérifier si la prestation existe déjà
        existing = Prestation.query.filter_by(
            nom=prestation_data['nom'],
            type_chaussure=prestation_data['type_chaussure']
        ).first()

        if existing:
            # Mettre à jour la prestation existante
            existing.prix = prestation_data['prix']
            existing.description = prestation_data['description']
            existing.image_filename = prestation_data['image_filename']
            existing.actif = prestation_data['actif']
            print(f"Mise à jour: {existing.nom} - {existing.type_chaussure.value} (Prix: {existing.prix}€)")
        else:
            # Créer une nouvelle prestation
            prestation = Prestation(**prestation_data)
            db.session.add(prestation)
            print(f"Création: {prestation.nom} - {prestation.type_chaussure.value} (Prix: {prestation.prix}€)")

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
