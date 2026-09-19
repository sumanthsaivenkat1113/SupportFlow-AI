# app/api/ticket_normaliser.py

import time

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.ticket_normaliser import (
    DeleteResponse,
    TicketNormalizationResponse,
)
from app.services import ticket_normaliser as service
from app.services import ticket_service

from app.models.workspaces import Workspace

router = APIRouter(
    prefix="/workspaces/{workspace_id}/tickets-normalization",
    tags=["Tickets Normalization"],
)


@router.post(
    "",
    response_model=TicketNormalizationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_tickets_normalization(
    workspace_id: UUID,
    db: Session = Depends(get_db),
):
    start_time = time.perf_counter()

    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()

    if workspace is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found.",
        )

    try:
        ticket_result = ticket_service.list_tickets_for_workspace(
            db=db,
            workspace=workspace,
            limit=200,
            offset=0,
        )

        tickets = ticket_result["tickets"]

        if not tickets:
            raise ValueError("No tickets found for this workspace.")

        record = await service.create_normalization(
            db=db,
            workspace_id=workspace_id,
            tickets=tickets,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    execution_time = round(time.perf_counter() - start_time, 2)

    return TicketNormalizationResponse(
        success=True,
        ticket_normalization_id=str(record.id),
        total_tickets=len(record.normalized_tickets),
        normalized_tickets=record.normalized_tickets,
        time_execution=execution_time,
    )


@router.get(
    "",
    response_model=TicketNormalizationResponse,
)
def get_tickets_normalization(
    workspace_id: UUID,
    db: Session = Depends(get_db),
):
    record = service.get_normalization(
        db=db,
        workspace_id=workspace_id,
    )

    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No normalization found for this workspace.",
        )

    return TicketNormalizationResponse(
        success=True,
        ticket_normalization_id=str(record.id),
        total_tickets=len(record.normalized_tickets),
        normalized_tickets=record.normalized_tickets,
    )


@router.delete(
    "",
    response_model=DeleteResponse,
)
def delete_tickets_normalization(
    workspace_id: UUID,
    db: Session = Depends(get_db),
):
    deleted = service.delete_normalizations(
        db=db,
        workspace_id=workspace_id,
    )

    if deleted == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No normalization found for this workspace.",
        )

    return DeleteResponse(
        success=True,
        message="Deleted successfully",
    )
