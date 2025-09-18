from database import db
from datetime import datetime
from enum import Enum

class StatutCommande(Enum):
    PENDING = 'pending'
    PAID = 'paid'
    PROCESSING = 'processing'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'

class Commande(db.Model):
    __tablename__ = 'commandes'

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    telephone = db.Column(db.String(20), nullable=False)
    entreprise = db.Column(db.String(100), nullable=False)
    statut = db.Column(db.Enum(StatutCommande), default=StatutCommande.PENDING, nullable=False)
    total = db.Column(db.Numeric(10, 2), nullable=False)
    stripe_payment_intent_id = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    paires = db.relationship('Paire', back_populates='commande', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Commande #{self.id} - {self.nom} - {self.statut.value}>'

    def calculate_total(self):
        total = 0
        for paire in self.paires:
            for paire_prestation in paire.paire_prestations:
                total += paire_prestation.prix_unitaire
        return total

    def to_dict(self):
        return {
            'id': self.id,
            'nom': self.nom,
            'email': self.email,
            'telephone': self.telephone,
            'entreprise': self.entreprise,
            'statut': self.statut.value,
            'total': float(self.total),
            'stripe_payment_intent_id': self.stripe_payment_intent_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'paires': [paire.to_dict() for paire in self.paires]
        }