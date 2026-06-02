"""matieres premieres + format sur articles

Revision ID: 0003
Revises: 0002
Create Date: 2026-06-02
"""
from alembic import op
import sqlalchemy as sa

revision = '0003'
down_revision = '0002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('articles', sa.Column('format', sa.String(50), nullable=True))

    op.create_table(
        'matieres_premieres',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('nom', sa.String(255), nullable=False),
        sa.Column('format', sa.String(50), nullable=False),
        sa.Column('unite', sa.String(50), nullable=False, server_default='feuille'),
    )
    op.create_index('idx_matieres_nom', 'matieres_premieres', ['nom'])


def downgrade() -> None:
    op.drop_table('matieres_premieres')
    op.drop_column('articles', 'format')
