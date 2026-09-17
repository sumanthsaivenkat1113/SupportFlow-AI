import uuid

from sqlalchemy import DateTime, String, UUID, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class TicketClassification(Base):

    __tablename__ = "ticket_classifications"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, index=True
    )

    model_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    items = relationship(
        "TicketClassificationItem",
        back_populates="classification",
        cascade="all, delete-orphan",
    )
