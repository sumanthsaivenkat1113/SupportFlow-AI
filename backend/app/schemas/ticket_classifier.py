from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class ClassifiedTicket(BaseModel):

    ticket_id: UUID
    subject: str
    classification: str
    confidence: float = Field(ge=0, le=1)
    reason: str


class TicketClassificationResponse(BaseModel):

    classification_id: UUID
    success: bool
    total_tickets: int
    classified_tickets: list[ClassifiedTicket]
    execution_time: float
