"""Initial migration

Revision ID: 001
Revises:
Create Date: 2025-09-18 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create ENUM types
    op.execute("CREATE TYPE typechaussure AS ENUM ('HOMME', 'FEMME')")
    op.execute("CREATE TYPE statutcommande AS ENUM ('PENDING', 'PAID', 'IN_PROGRESS', 'READY', 'DELIVERED', 'CANCELLED')")

    # Create commandes table
    op.create_table('commandes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('numero_commande', sa.String(length=50), nullable=False),
        sa.Column('nom', sa.String(length=100), nullable=False),
        sa.Column('prenom', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=150), nullable=False),
        sa.Column('telephone', sa.String(length=20), nullable=True),
        sa.Column('adresse', sa.Text(), nullable=True),
        sa.Column('total', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('statut', sa.Enum('PENDING', 'PAID', 'IN_PROGRESS', 'READY', 'DELIVERED', 'CANCELLED', name='statutcommande'), nullable=False),
        sa.Column('stripe_payment_intent_id', sa.String(length=200), nullable=True),
        sa.Column('stripe_session_id', sa.String(length=200), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('numero_commande')
    )

    # Create prestations table
    op.create_table('prestations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nom', sa.String(length=100), nullable=False),
        sa.Column('prix', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('type_chaussure', sa.Enum('HOMME', 'FEMME', name='typechaussure'), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('actif', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create paires table
    op.create_table('paires',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('commande_id', sa.Integer(), nullable=False),
        sa.Column('type_chaussure', sa.Enum('HOMME', 'FEMME', name='typechaussure'), nullable=False),
        sa.Column('photo_url', sa.String(length=500), nullable=True),
        sa.Column('photo_gcs_path', sa.String(length=500), nullable=True),
        sa.Column('commentaires', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['commande_id'], ['commandes.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create paire_prestations table
    op.create_table('paire_prestations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('paire_id', sa.Integer(), nullable=False),
        sa.Column('prestation_id', sa.Integer(), nullable=False),
        sa.Column('prix_unitaire', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['paire_id'], ['paires.id'], ),
        sa.ForeignKeyConstraint(['prestation_id'], ['prestations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('paire_prestations')
    op.drop_table('paires')
    op.drop_table('prestations')
    op.drop_table('commandes')
    op.execute('DROP TYPE statutcommande')
    op.execute('DROP TYPE typechaussure')