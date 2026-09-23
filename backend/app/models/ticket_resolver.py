import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.tickets import Ticket  # your existing Ticket model


class TicketResolution(Base):
    __tablename__ = "ticket_resolutions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    ticket_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tickets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # AI-generated response
    response: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    # Retrieved policy/context used by AI
    context: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Model used for generation
    model_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # generated | approved | rejected | edited
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        server_default=text("'generated'"),
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    ticket = relationship("Ticket", back_populates="resolutions")
