# app/api/ticket_classifier.py

import logging
import time
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.core.database import get_db

from app.models.ticket_classification import (
    TicketClassification,
)

from app.models.workspaces import (
    Workspace,
)

from app.schemas.ticket_classifier import (
    TicketClassificationResponse,
)

from app.services import (
    ticket_classifier as service,
)

# ============================================================
# LOGGER
# ============================================================

logger = logging.getLogger(__name__)


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/workspaces/{workspace_id}/ticket-classifications",
    tags=["Ticket Classification"],
)


# ============================================================
# POST
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

    # --------------------------------------------------------
    # 1. Check workspace
    # --------------------------------------------------------

    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()

    if workspace is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found.",
        )

    # --------------------------------------------------------
    # 2. Create classification
    # --------------------------------------------------------

    try:

        record = await service.create_classification(
            db=db,
            workspace_id=workspace_id,
        )

    except ValueError as exc:

        logger.exception("Classification validation error")

        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except Exception as exc:

        # IMPORTANT:
        # Print the actual error in development.
        logger.exception("Ticket classification failed")

        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to classify tickets: {str(exc)}",
        ) from exc

    # --------------------------------------------------------
    # 3. Execution time
    # --------------------------------------------------------

    execution_time = round(
        time.perf_counter() - start_time,
        2,
    )

    # --------------------------------------------------------
    # 4. Build response
    # --------------------------------------------------------

    classified_tickets = []

    for item in record.items:

        classified_tickets.append(
            {
                "ticket_id": str(item.ticket_id),
                "classification": (item.classification),
                "confidence": (
                    float(item.confidence) if item.confidence is not None else 0.0
                ),
                "reason": (item.reason or ""),
            }
        )

    # --------------------------------------------------------
    # 5. Return response
    # --------------------------------------------------------

    return TicketClassificationResponse(
        classification_id=str(record.id),
        success=True,
        total_tickets=len(classified_tickets),
        classified_tickets=(classified_tickets),
        execution_time=(execution_time),
    )


# ============================================================
# GET
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

    # --------------------------------------------------------
    # Find classification
    # --------------------------------------------------------

    record = (
        db.query(TicketClassification)
        .filter(
            TicketClassification.id == classification_id,
            TicketClassification.workspace_id == workspace_id,
        )
        .first()
    )

    if record is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Classification not found.",
        )

    # --------------------------------------------------------
    # Build response
    # --------------------------------------------------------

    classified_tickets = []

    for item in record.items:

        classified_tickets.append(
            {
                "ticket_id": str(item.ticket_id),
                "classification": (item.classification),
                "confidence": (
                    float(item.confidence) if item.confidence is not None else 0.0
                ),
                "reason": (item.reason or ""),
            }
        )

    # --------------------------------------------------------
    # Execution time
    # --------------------------------------------------------

    execution_time = round(
        time.perf_counter() - start_time,
        2,
    )

    return TicketClassificationResponse(
        classification_id=str(record.id),
        success=True,
        total_tickets=len(classified_tickets),
        classified_tickets=(classified_tickets),
        execution_time=(execution_time),
    )
