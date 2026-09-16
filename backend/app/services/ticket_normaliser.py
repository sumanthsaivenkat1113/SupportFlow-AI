from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.ai.ticket_normaliser import (
    normalize_tickets as ai_normalize_tickets,
)
from app.models.ticket_normaliser import TicketNormalization


async def create_normalization(
    db: Session,
    workspace_id: UUID,
    tickets: list[dict],
) -> TicketNormalization:
    # ---------------------------------------------------------
    # 1. Get normalized tickets from AI
    #
    # AI format:
    # {
    #     "id": "...",
    #     "description": "..."
    # }
    # ---------------------------------------------------------
    ai_normalized = await ai_normalize_tickets(tickets)

    # ---------------------------------------------------------
    # 2. Convert AI format to API/database format
    #
    # API format:
    # {
    #     "ticket_id": "...",
    #     "description": "..."
    # }
    # ---------------------------------------------------------
    normalized_tickets = []

    for ticket in ai_normalized:
        normalized_tickets.append(
            {
                "ticket_id": ticket["id"],
                "description": ticket["description"],
            }
        )

    # ---------------------------------------------------------
    # 3. Save normalized tickets
    # ---------------------------------------------------------
    record = TicketNormalization(
        workspace_id=workspace_id,
        normalized_tickets=normalized_tickets,
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return record


def get_normalization(
    db: Session,
    workspace_id: UUID,
) -> TicketNormalization | None:
    stmt = (
        select(TicketNormalization)
        .where(TicketNormalization.workspace_id == workspace_id)
        .order_by(TicketNormalization.created_at.desc())
        .limit(1)
    )

    result = db.execute(stmt)

    return result.scalar_one_or_none()


def delete_normalizations(
    db: Session,
    workspace_id: UUID,
) -> int:
    stmt = delete(TicketNormalization).where(
        TicketNormalization.workspace_id == workspace_id
    )

    result = db.execute(stmt)

    db.commit()

    return result.rowcount or 0
