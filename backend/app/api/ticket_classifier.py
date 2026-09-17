# app/api/ticket_classifier.py

import logging
import time
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.orm import Session

from app.core.database import get_db

from app.schemas.ticket_classifier import (
    GlobalClassifiedTicket,
    GlobalTicketClassification,
    GlobalTicketClassificationListResponse,
    TicketClassificationResponse,
)

from app.services import (
    ticket_classifier as service,
)
from app.services.exceptions import (
    NotFoundError,
    ValidationError,
)

# ============================================================
# LOGGER
# ============================================================

logger = logging.getLogger(__name__)


# ============================================================
# ROUTERS
# ============================================================

# Workspace-scoped: POST + GET one
router = APIRouter(
    prefix="/workspaces/{workspace_id}/ticket-classifications",
    tags=["Ticket Classification"],
)

# Global: list all classifications across all workspaces
global_router = APIRouter(
    prefix="/workspaces/ticket-classifications",
    tags=["Ticket Classification"],
)


# ============================================================
# HELPERS (pure translation, no DB)
# ============================================================


def _detail_to_response(
    detail: service.ClassificationDetail,
    execution_time: float,
) -> TicketClassificationResponse:

    return TicketClassificationResponse(
        classification_id=str(detail.classification_id),
        success=True,
        total_tickets=detail.total_tickets,
        classified_tickets=[
            {
                "ticket_id": str(ticket.ticket_id),
                "classification": ticket.classification,
                "confidence": ticket.confidence,
                "reason": ticket.reason,
            }
            for ticket in detail.tickets
        ],
        execution_time=execution_time,
    )


def _global_to_response(
    item: service.GlobalClassification,
) -> GlobalTicketClassification:

    return GlobalTicketClassification(
        classification_id=str(item.classification_id),
        workspace_id=str(item.workspace_id),
        workspace_name=item.workspace_name,
        model_name=item.model_name,
        created_at=item.created_at,
        total_tickets=item.total_tickets,
        classified_tickets=[
            GlobalClassifiedTicket(
                ticket_id=str(ticket.ticket_id),
                classification=ticket.classification,
                confidence=ticket.confidence,
                reason=ticket.reason,
            )
            for ticket in item.tickets
        ],
    )


def _raise_http_from_service(exc: Exception) -> None:
    """Map a domain exception to the corresponding HTTPException."""

    if isinstance(exc, NotFoundError):

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    if isinstance(exc, ValidationError):

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    logger.exception("Unexpected service error")

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Internal error: {exc}",
    ) from exc


# ============================================================
# GLOBAL — GET (list all classifications across all workspaces)
# ============================================================


@global_router.get(
    "",
    response_model=GlobalTicketClassificationListResponse,
)
def list_all_ticket_classifications(
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):

    start_time = time.perf_counter()

    try:

        results, total = service.list_all_classifications(
            db=db,
            limit=limit,
            offset=offset,
        )

    except Exception as exc:

        _raise_http_from_service(exc)

    execution_time = round(
        time.perf_counter() - start_time,
        2,
    )

    return GlobalTicketClassificationListResponse(
        success=True,
        total=total,
        classifications=[_global_to_response(item) for item in results],
        execution_time=execution_time,
    )


# ============================================================
# WORKSPACE — POST (create a classification run)
# ============================================================


@router.post(
    "",
    response_model=TicketClassificationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_ticket_classification(
    workspace_id: UUID,
    db: Session = Depends(get_db),
):

    start_time = time.perf_counter()

    try:

        detail = await service.create_classification(
            db=db,
            workspace_id=workspace_id,
        )

    except Exception as exc:

        _raise_http_from_service(exc)

    execution_time = round(
        time.perf_counter() - start_time,
        2,
    )

    return _detail_to_response(detail, execution_time)


# ============================================================
# WORKSPACE — GET (one classification)
# ============================================================


@router.get(
    "/{classification_id}",
    response_model=TicketClassificationResponse,
)
def get_ticket_classification(
    workspace_id: UUID,
    classification_id: UUID,
    db: Session = Depends(get_db),
):

    start_time = time.perf_counter()

    try:

        detail = service.get_classification(
            db=db,
            workspace_id=workspace_id,
            classification_id=classification_id,
        )

    except Exception as exc:

        _raise_http_from_service(exc)

    execution_time = round(
        time.perf_counter() - start_time,
        2,
    )

    return _detail_to_response(detail, execution_time)
