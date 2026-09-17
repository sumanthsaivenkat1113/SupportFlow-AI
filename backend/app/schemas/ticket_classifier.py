# app/schemas/ticket_classifier.py

from pydantic import BaseModel, Field


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
