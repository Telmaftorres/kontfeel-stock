"""add etude_ref to movements

Revision ID: 0004
Revises: 0003
Create Date: 2026-06-02
"""
from alembic import op
import sqlalchemy as sa

revision = '0004'
down_revision = '0003'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('movements', sa.Column('etude_ref', sa.String(50), nullable=True, index=True))


def downgrade():
    op.drop_column('movements', 'etude_ref')
