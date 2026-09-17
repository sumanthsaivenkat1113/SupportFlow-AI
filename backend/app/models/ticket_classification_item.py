import uuid
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, UUID, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class TicketClassificationItem(Base):

    __tablename__ = "ticket_classification_items"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    classification_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ticket_classifications.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    ticket_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tickets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    classification: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    confidence: Mapped[Decimal | None] = mapped_column(Numeric(5, 4), nullable=True)

    reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    classification = relationship("TicketClassification", back_populates="items")
