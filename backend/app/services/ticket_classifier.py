import asyncio
from uuid import UUID

from sqlalchemy.orm import Session

from app.ai.ticket_classifier import (
    classify_tickets,
)
from app.models.ticket_classification import (
    TicketClassification,
)
from app.models.ticket_classification_item import (
    TicketClassificationItem,
)
from app.services.ticket_normaliser import (
    get_normalization,
)

# ============================================================
# CONFIGURATION
# ============================================================

MODEL_NAME = "qwen/qwen3.8-27b"


# ============================================================
# CREATE CLASSIFICATION
# ============================================================


async def create_classification(
    db: Session,
    workspace_id: UUID,
) -> TicketClassification:

    # --------------------------------------------------------
    # 1. Get latest normalization
    # --------------------------------------------------------

    normalization = get_normalization(
        db=db,
        workspace_id=workspace_id,
    )

    if normalization is None:
        raise ValueError("No normalization found for this workspace.")

    # --------------------------------------------------------
    # 2. Get normalized tickets
    # --------------------------------------------------------

    normalized_tickets = normalization.normalized_tickets

    if not normalized_tickets:
        raise ValueError("No normalized tickets found for this workspace.")

    # --------------------------------------------------------
    # 3. Classify all tickets in ONE Groq request
    # --------------------------------------------------------

    classified = await asyncio.to_thread(
        classify_tickets,
        normalized_tickets,
    )

    if not classified:
        raise ValueError("No tickets were classified.")

    # --------------------------------------------------------
    # 4. Create classification run
    # --------------------------------------------------------

    record = TicketClassification(
        workspace_id=workspace_id,
        model_name=MODEL_NAME,
    )

    db.add(record)

    # Generate UUID for parent before creating children.
    db.flush()

    # --------------------------------------------------------
    # 5. Save classification items
    # --------------------------------------------------------

    for result in classified:

        item = TicketClassificationItem(
            classification_id=record.id,
            ticket_id=UUID(result["ticket_id"]),
            classification=result["classification"],
            confidence=result["confidence"],
            reason=result["reason"],
        )

        db.add(item)

    # --------------------------------------------------------
    # 6. Commit
    # --------------------------------------------------------

    try:

        db.commit()

    except Exception:

        db.rollback()

        raise

    # --------------------------------------------------------
    # 7. Refresh
    # --------------------------------------------------------

    db.refresh(record)

    return record
