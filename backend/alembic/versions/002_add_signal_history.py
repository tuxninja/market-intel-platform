"""add signal history table

Revision ID: 002
Revises: 001
Create Date: 2025-10-22

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add signal_history table for deduplication."""
    op.create_table(
        'signal_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('symbol', sa.String(10), nullable=False, index=True),
        sa.Column('signal_type', sa.String(20), nullable=False),  # 'bullish', 'bearish', 'neutral'
        sa.Column('confidence_score', sa.Float(), nullable=False),
        sa.Column('news_article_id', sa.String(255), nullable=True),  # Hash of article URL
        sa.Column('news_title', sa.Text(), nullable=True),
        sa.Column('sentiment_score', sa.Float(), nullable=True),
        sa.Column('technical_score', sa.Float(), nullable=True),
        sa.Column('price_at_signal', sa.Float(), nullable=True),
        sa.Column('metadata', JSONB, nullable=True),  # Additional data
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('expires_at', sa.DateTime(), nullable=False),  # When signal should be considered stale
        sa.PrimaryKeyConstraint('id')
    )

    # Create index for efficient lookups
    op.create_index(
        'idx_signal_history_symbol_created',
        'signal_history',
        ['symbol', 'created_at']
    )
    op.create_index(
        'idx_signal_history_expires',
        'signal_history',
        ['expires_at']
    )


def downgrade() -> None:
    """Remove signal_history table."""
    op.drop_index('idx_signal_history_expires')
    op.drop_index('idx_signal_history_symbol_created')
    op.drop_table('signal_history')
