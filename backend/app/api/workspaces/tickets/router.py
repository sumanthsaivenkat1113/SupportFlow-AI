from typing import Annotated

from fastapi import APIRouter, Depends, File, Query, UploadFile
from sqlalchemy.orm import Session

from app.api.workspaces.deps import (
    OwnedTicket,
    OwnedTicketImport,
    OwnedWorkspace,
)
from app.core.database import get_db
from app.schemas.ticket import (
    TicketDeleteResponse,
    TicketImportCreateResponse,
    TicketImportStatusResponse,
    TicketListResponse,
)
from app.services import ticket_service

router = APIRouter(tags=["Tickets"])


# ============================================================
# POST /api/workspaces/{workspace_id}/ticket-imports
# ============================================================


@router.post(
    "/{workspace_id}/ticket-imports",
    response_model=TicketImportCreateResponse,
)
async def create_ticket_import(
    workspace: OwnedWorkspace,
    db: Annotated[Session, Depends(get_db)],
    customer_tickets_file: Annotated[UploadFile, File(...)],
):
    return await ticket_service.create_ticket_import(
        db=db,
        workspace=workspace,
        upload=customer_tickets_file,
    )


# ============================================================
# GET /api/workspaces/{workspace_id}/ticket-imports/{import_id}
# ============================================================


@router.get("/{workspace_id}/ticket-imports/{import_id}")
def get_ticket_import(
    ticket_import: OwnedTicketImport,
    db: Annotated[Session, Depends(get_db)],
):
    return ticket_service.get_ticket_import_details(
        db=db,
        ticket_import=ticket_import,
    )


# ============================================================
# GET /api/workspaces/{workspace_id}/ticket-imports/{import_id}/status
# ============================================================


@router.get(
    "/{workspace_id}/ticket-imports/{import_id}/status",
    response_model=TicketImportStatusResponse,
)
def get_ticket_import_status(
    ticket_import: OwnedTicketImport,
):
    return ticket_service.get_ticket_import_status(ticket_import=ticket_import)


# ============================================================
# GET /api/workspaces/{workspace_id}/tickets
# ============================================================


@router.get(
    "/{workspace_id}/tickets",
    response_model=TicketListResponse,
)
def list_tickets(
    workspace: OwnedWorkspace,
    db: Annotated[Session, Depends(get_db)],
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    return ticket_service.list_tickets_for_workspace(
        db=db,
        workspace=workspace,
        limit=limit,
        offset=offset,
    )


# ============================================================
# GET /api/workspaces/{workspace_id}/tickets/{ticket_id}
# ============================================================


@router.get("/{workspace_id}/tickets/{ticket_id}")
def get_ticket(
    ticket: OwnedTicket,
):
    return ticket_service.get_ticket_details(ticket=ticket)


# ============================================================
# DELETE /api/workspaces/{workspace_id}/tickets/{ticket_id}
# ============================================================


@router.delete(
    "/{workspace_id}/tickets/{ticket_id}",
    response_model=TicketDeleteResponse,
)
def delete_ticket(
    ticket: OwnedTicket,
    db: Annotated[Session, Depends(get_db)],
):
    return ticket_service.delete_ticket(db=db, ticket=ticket)
