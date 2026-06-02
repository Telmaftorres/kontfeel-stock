"""init

Revision ID: 0001
Revises:
Create Date: 2026-06-02
"""
from alembic import op
import sqlalchemy as sa

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'api_keys',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('key_hash', sa.String(64), unique=True, nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        'articles',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('ref', sa.String(50), unique=True, nullable=False),
        sa.Column('nom', sa.String(255), nullable=False),
        sa.Column('zone', sa.String(50), nullable=False),
        sa.Column('unite', sa.String(50), nullable=False, default='unité'),
        sa.Column('conditionnement', sa.String(50), nullable=False, default='aucun'),
        sa.Column('stock_actuel', sa.Numeric(12, 3), nullable=False, default=0),
        sa.Column('stock_mini', sa.Numeric(12, 3), nullable=False, default=0),
        sa.Column('prix_unitaire', sa.Numeric(12, 2), nullable=True),
        sa.Column('photos', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('idx_articles_ref', 'articles', ['ref'])
    op.create_index('idx_articles_zone', 'articles', ['zone'])

    op.create_table(
        'movements',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('article_ref', sa.String(50), sa.ForeignKey('articles.ref'), nullable=False),
        sa.Column('type', sa.String(10), nullable=False),
        sa.Column('quantite', sa.Numeric(12, 3), nullable=False),
        sa.Column('stock_avant', sa.Numeric(12, 3), nullable=False),
        sa.Column('stock_apres', sa.Numeric(12, 3), nullable=False),
        sa.Column('cout', sa.Numeric(12, 2), nullable=True),
        sa.Column('employe', sa.String(100), nullable=False, default='Anonyme'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('source', sa.String(50), nullable=False, default='stock-app'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('idx_movements_ref', 'movements', ['article_ref'])
    op.create_index('idx_movements_date', 'movements', ['created_at'])

    op.create_table(
        'webhooks',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('url', sa.String(500), nullable=False),
        sa.Column('secret', sa.String(100), nullable=True),
        sa.Column('events', sa.String(200), nullable=False, default='movement'),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        'webhook_logs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('webhook_id', sa.Integer(), sa.ForeignKey('webhooks.id'), nullable=False),
        sa.Column('event', sa.String(50), nullable=False),
        sa.Column('status_code', sa.Integer(), nullable=True),
        sa.Column('error', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('webhook_logs')
    op.drop_table('webhooks')
    op.drop_table('movements')
    op.drop_table('articles')
    op.drop_table('api_keys')
