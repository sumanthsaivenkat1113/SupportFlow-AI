from typing import Any, Dict, List
from uuid import UUID

from pydantic import BaseModel, Field


class TicketIn(BaseModel):
    id: UUID
    workspace_id: UUID
    import_id: UUID | None = None
    customer_ticket: Dict[str, Any] = Field(default_factory=dict)
    created_at: str | None = None
    updated_at: str | None = None


class TicketNormalizationRequest(BaseModel):
    tickets: List[TicketIn] = Field(..., min_length=1, max_length=20)


class NormalizedTicket(BaseModel):
    ticket_id: str
    description: str


class TicketNormalizationResponse(BaseModel):
    success: bool = True
    ticket_normalization_id: str
    total_tickets: int
    normalized_tickets: List[NormalizedTicket]
    time_execution: float | None = None


class DeleteResponse(BaseModel):
    success: bool = True
    message: str = "deleted successfully"
