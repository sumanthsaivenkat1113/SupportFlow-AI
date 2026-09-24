import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

# ---------- Request ----------


class TicketResolutionRequest(BaseModel):
    """Trigger resolution generation for a workspace."""

    workspace_id: uuid.UUID
    batch_size: int = Field(
        default=5,
        ge=1,
        le=20,
    )
    top_k: int = Field(
        default=3,
        ge=1,
        le=10,
    )


# ---------- Normalized ticket input ----------


class NormalizedTicket(BaseModel):
    ticket_id: str  # external id e.g. "F3-3001"
    description: str


# ---------- Internal resolution result ----------


class TicketResolutionResult(BaseModel):
    ticket_id: str  # external id e.g. "F3-3001"

    external_customer_id: str | None = None

    ticket_resolution: str

    # AI classification:
    # "ai-automated" | "human-required"
    generated: str

    context: str | None = None

    model_name: str | None = None

    error: str | None = None

    timing: dict[str, float] | None = None


# ---------- Persisted row ----------


class TicketResolutionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID

    ticket_id: uuid.UUID

    response: str

    # AI classification:
    # "ai-automated" | "human-required"
    generated: str

    context: str | None

    model_name: str | None

    status: str

    created_at: datetime


# ---------- Batch API response ----------


class TicketResolutionBatchResponse(BaseModel):
    success: bool

    workspace_id: uuid.UUID

    total_tickets: int

    total_batches: int

    batch_size: int

    resolutions: list[dict[str, Any]]

    time_execution: float | None = None
