"""Add image_filename to prestations

Revision ID: 002
Revises: 001
Create Date: 2025-09-22 23:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    # Add image_filename column to prestations table
    op.add_column('prestations', sa.Column('image_filename', sa.String(length=255), nullable=True))


def downgrade():
    # Remove image_filename column from prestations table
    op.drop_column('prestations', 'image_filename')