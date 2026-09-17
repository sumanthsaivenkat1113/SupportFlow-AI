"""add classification column to ticket classification items

Revision ID: bfde27dd5e25
Revises: fd64c93d450b
Create Date: 2026-09-17 18:07:08.053550

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "bfde27dd5e25"
down_revision: Union[str, Sequence[str], None] = "fd64c93d450b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "ticket_classification_items",
        sa.Column(
            "classification",
            sa.String(length=50),
            nullable=False,
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column(
        "ticket_classification_items",
        "classification",
    )
