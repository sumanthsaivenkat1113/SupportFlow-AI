"""add generated to ticket_resolutions

Revision ID: 40b2699764e0
Revises: cfc138c2f4c8
Create Date: 2026-09-24 15:12:21.743731

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "40b2699764e0"
down_revision: Union[str, Sequence[str], None] = "cfc138c2f4c8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add column as nullable first so existing rows don't violate NOT NULL
    op.add_column(
        "ticket_resolutions",
        sa.Column("generated", sa.String(length=50), nullable=True),
    )

    # Backfill existing rows with a sensible default
    op.execute("UPDATE ticket_resolutions SET generated = '' WHERE generated IS NULL")

    # Now enforce NOT NULL
    op.alter_column("ticket_resolutions", "generated", nullable=False)

    # Index
    op.create_index(
        op.f("ix_ticket_resolutions_generated"),
        "ticket_resolutions",
        ["generated"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        op.f("ix_ticket_resolutions_generated"), table_name="ticket_resolutions"
    )
    op.drop_column("ticket_resolutions", "generated")
