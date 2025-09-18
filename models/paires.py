from database import db
from datetime import datetime
from .enums import TypeChaussure

class Paire(db.Model):
    __tablename__ = 'paires'

    id = db.Column(db.Integer, primary_key=True)
    commande_id = db.Column(db.Integer, db.ForeignKey('commandes.id'), nullable=False)
    type_chaussure = db.Column(db.Enum(TypeChaussure), nullable=False)
    photo_url = db.Column(db.String(500))
    photo_gcs_path = db.Column(db.String(500))
    photo_filename = db.Column(db.String(200))
    description = db.Column(db.Text)
    ordre = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    commande = db.relationship('Commande', back_populates='paires')
    paire_prestations = db.relationship('PairePrestation', back_populates='paire', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Paire #{self.id} - {self.type_chaussure.value} - Commande #{self.commande_id}>'

    def get_total_prix(self):
        return sum(pp.prix_unitaire for pp in self.paire_prestations)

    def to_dict(self):
        return {
            'id': self.id,
            'commande_id': self.commande_id,
            'type_chaussure': self.type_chaussure.value,
            'photo_url': self.photo_url,
            'photo_filename': self.photo_filename,
            'description': self.description,
            'ordre': self.ordre,
            'created_at': self.created_at.isoformat(),
            'prestations': [pp.to_dict() for pp in self.paire_prestations],
            'total_prix': float(self.get_total_prix())
        }

class PairePrestation(db.Model):
    __tablename__ = 'paire_prestations'

    id = db.Column(db.Integer, primary_key=True)
    paire_id = db.Column(db.Integer, db.ForeignKey('paires.id'), nullable=False)
    prestation_id = db.Column(db.Integer, db.ForeignKey('prestations.id'), nullable=False)
    prix_unitaire = db.Column(db.Numeric(10, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    paire = db.relationship('Paire', back_populates='paire_prestations')
    prestation = db.relationship('Prestation', back_populates='paire_prestations')

    def __repr__(self):
        return f'<PairePrestation #{self.id} - Paire #{self.paire_id} - Prestation #{self.prestation_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'paire_id': self.paire_id,
            'prestation_id': self.prestation_id,
            'prestation_nom': self.prestation.nom if self.prestation else None,
            'prix_unitaire': float(self.prix_unitaire),
            'created_at': self.created_at.isoformat()
        }