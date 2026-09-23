import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.ticket_resolver import (
    TicketResolutionBatchResponse,
    TicketResolutionRead,
)
from app.services.ticket_resolver import resolve_workspace_tickets

router = APIRouter(
    prefix="/workspaces/{workspace_id}/ticket-resolutions",
    tags=["ticket-resolutions"],
)


@router.post(
    "",
    response_model=TicketResolutionBatchResponse,
    status_code=status.HTTP_200_OK,
)
async def generate_ticket_resolutions(
    workspace_id: uuid.UUID,
    batch_size: int = 5,
    top_k: int = 3,
    db: Session = Depends(get_db),
):
    """
    Generate AI ticket resolutions for all normalized tickets in a workspace.

    Pipeline:
      normalized tickets → embeddings → retrieval → context → LLM
      → persisted ticket_resolutions (ticket_id transformed to UUID).

    Processes tickets in batches (default 5) with concurrent LLM calls.
    """
    result = await resolve_workspace_tickets(
        db=db,
        workspace_id=workspace_id,
        batch_size=batch_size,
        top_k=top_k,
    )

    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No normalized tickets found for this workspace.",
        )

    return result


@router.get(
    "",
    response_model=list[TicketResolutionRead],
)
def list_ticket_resolutions(
    workspace_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    """
    List all persisted ticket resolutions for a workspace.
    """
    from app.models import Ticket, TicketResolution

    rows = (
        db.query(TicketResolution)
        .join(Ticket, Ticket.id == TicketResolution.ticket_id)
        .filter(Ticket.workspace_id == workspace_id)
        .order_by(TicketResolution.created_at.desc())
        .all()
    )
    return rows
