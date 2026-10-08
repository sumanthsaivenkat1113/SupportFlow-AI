"""create ticket resolution

Revision ID: cfc138c2f4c8
Revises: bfde27dd5e25
Create Date: 2026-09-23 10:19:35.156958

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "cfc138c2f4c8"
down_revision: Union[str, Sequence[str], None] = "bfde27dd5e25"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create ticket_resolutions table."""

    op.create_table(
        "ticket_resolutions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column(
            "ticket_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "response",
            sa.Text(),
            nullable=False,
        ),
        sa.Column(
            "context",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "model_name",
            sa.String(length=255),
            nullable=True,
        ),
        sa.Column(
            "status",
            sa.String(length=50),
            server_default=sa.text("'generated'"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["ticket_id"],
            ["tickets.id"],
            name="ticket_resolutions_ticket_id_fkey",
            ondelete="CASCADE",
        ),
    )

    op.create_index(
        op.f("ix_ticket_resolutions_ticket_id"),
        "ticket_resolutions",
        ["ticket_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_ticket_resolutions_status"),
        "ticket_resolutions",
        ["status"],
        unique=False,
    )


def downgrade() -> None:
    """Drop ticket_resolutions table."""

    op.drop_index(
        op.f("ix_ticket_resolutions_status"),
        table_name="ticket_resolutions",
    )

    op.drop_index(
        op.f("ix_ticket_resolutions_ticket_id"),
        table_name="ticket_resolutions",
    )

    op.drop_table("ticket_resolutions")
