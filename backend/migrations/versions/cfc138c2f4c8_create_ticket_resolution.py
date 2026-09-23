"""create ticket resolution

Revision ID: cfc138c2f4c8
Revises: bfde27dd5e25
Create Date: 2026-09-23 10:19:35.156958

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "cfc138c2f4c8"
down_revision: Union[str, Sequence[str], None] = "bfde27dd5e25"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.drop_constraint(
        "ticket_resolutions_ticket_id_fkey",
        "ticket_resolutions",
        type_="foreignkey",
    )

    op.create_foreign_key(
        "ticket_resolutions_ticket_id_fkey",
        "ticket_resolutions",
        "tickets",
        ["ticket_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_constraint(
        "ticket_resolutions_ticket_id_fkey",
        "ticket_resolutions",
        type_="foreignkey",
    )

    op.create_foreign_key(
        "ticket_resolutions_ticket_id_fkey",
        "ticket_resolutions",
        "tickets",
        ["ticket_id"],
        ["id"],
    )
