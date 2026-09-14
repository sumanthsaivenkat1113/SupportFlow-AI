"""add document chunks and embeddings

Revision ID: ae5b73b38816
Revises: 851b8a8ce57e
Create Date: 2026-09-14 23:28:30.398536

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from pgvector.sqlalchemy import VECTOR

# revision identifiers, used by Alembic.
revision: str = "ae5b73b38816"
down_revision: Union[str, Sequence[str], None] = "851b8a8ce57e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Enable pgvector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "document_chunks",
        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column(
            "document_id",
            sa.UUID(),
            nullable=False,
        ),
        sa.Column(
            "workspace_id",
            sa.UUID(),
            nullable=False,
        ),
        sa.Column(
            "chunk_index",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "content",
            sa.Text(),
            nullable=False,
        ),
        sa.Column(
            "token_count",
            sa.Integer(),
            nullable=True,
        ),
        sa.Column(
            "embedding",
            VECTOR(768),
            nullable=False,
        ),
        sa.Column(
            "metadata",
            sa.JSON(),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["document_id"],
            ["documents.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["workspaces.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_document_chunks_document_id"),
        "document_chunks",
        ["document_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_document_chunks_workspace_id"),
        "document_chunks",
        ["workspace_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        op.f("ix_document_chunks_workspace_id"),
        table_name="document_chunks",
    )

    op.drop_index(
        op.f("ix_document_chunks_document_id"),
        table_name="document_chunks",
    )

    op.drop_table("document_chunks")
