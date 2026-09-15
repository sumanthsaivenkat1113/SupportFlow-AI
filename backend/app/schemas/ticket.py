from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict

# ---------- Ticket imports ----------


class TicketImportSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workspace_id: UUID
    file_name: str | None
    file_type: str | None
    status: str
    total_tickets: int
    processed_tickets: int
    failed_tickets: int
    error_message: str | None
    created_at: datetime
    updated_at: datetime


class TicketImportCreateResponse(BaseModel):
    success: bool
    message: str
    import_id: UUID
    workspace_id: UUID
    file_name: str | None
    file_type: str | None
    status: str
    total_tickets: int
    processed_tickets: int
    failed_tickets: int


class TicketImportStatusResponse(BaseModel):
    success: bool
    import_id: UUID
    status: str
    progress: dict[str, int]
    error_message: str | None


# ---------- Tickets ----------


class TicketSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workspace_id: UUID
    import_id: UUID
    customer_ticket: dict[str, Any]
    created_at: datetime
    updated_at: datetime


class TicketListResponse(BaseModel):
    success: bool
    workspace_id: UUID
    total_tickets: int
    tickets: list[TicketSummary]


class TicketDeleteResponse(BaseModel):
    success: bool
    message: str
    workspace_id: UUID
    ticket_id: UUID
