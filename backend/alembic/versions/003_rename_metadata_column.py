"""rename metadata to signal_metadata in signal_history

Revision ID: 003
Revises: 002
Create Date: 2025-10-24

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Rename metadata column to signal_metadata to avoid SQLAlchemy reserved name conflict."""
    op.alter_column(
        'signal_history',
        'metadata',
        new_column_name='signal_metadata'
    )


def downgrade() -> None:
    """Rename signal_metadata back to metadata."""
    op.alter_column(
        'signal_history',
        'signal_metadata',
        new_column_name='metadata'
    )
