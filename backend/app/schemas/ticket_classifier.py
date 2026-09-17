# app/schemas/ticket_classifier.py

from pydantic import BaseModel, Field
from datetime import datetime


class ClassifiedTicketResponse(BaseModel):

    ticket_id: str

    classification: str = Field(
        ...,
        description="automatable or human_review",
    )

    confidence: float = Field(
        ...,
        ge=0,
        le=1,
    )

    reason: str


class TicketClassificationResponse(BaseModel):

    classification_id: str

    success: bool

    total_tickets: int

    classified_tickets: list[ClassifiedTicketResponse]

    execution_time: float


class GlobalClassifiedTicket(BaseModel):

    ticket_id: str

    classification: str

    confidence: float

    reason: str


class GlobalTicketClassification(BaseModel):

    classification_id: str

    workspace_id: str

    workspace_name: str

    model_name: str | None

    created_at: datetime

    total_tickets: int

    classified_tickets: list[GlobalClassifiedTicket]


class GlobalTicketClassificationListResponse(BaseModel):

    success: bool

    total: int

    classifications: list[GlobalTicketClassification]

    execution_time: float
