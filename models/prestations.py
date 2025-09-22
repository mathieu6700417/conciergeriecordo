from database import db
from datetime import datetime
from .enums import TypeChaussure

class Prestation(db.Model):
    __tablename__ = 'prestations'

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    prix = db.Column(db.Numeric(10, 2), nullable=False)
    type_chaussure = db.Column(db.Enum(TypeChaussure), nullable=False)
    description = db.Column(db.Text)
    image_filename = db.Column(db.String(255), nullable=True)
    actif = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    paire_prestations = db.relationship('PairePrestation', back_populates='prestation', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Prestation {self.nom} - {self.type_chaussure.value}>'

    def to_dict(self):
        return {
            'id': self.id,
            'nom': self.nom,
            'prix': float(self.prix),
            'type_chaussure': self.type_chaussure.value,
            'description': self.description,
            'image_filename': self.image_filename,
            'actif': self.actif,
            'created_at': self.created_at.isoformat()
        }