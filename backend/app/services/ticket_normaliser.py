from uuid import UUID

from sqlalchemy.orm import Session

from app.models.ticket_normaliser import TicketNormalization

# from app.ai.ticket_normalise import normalize_tickets
from app.ai.ticket_normaliser import normalize_tickets


async def create_normalization(
    db: Session,
    workspace_id: UUID,
    tickets: list[dict],
) -> TicketNormalization:

    # ---------------------------------------------------------
    # 1. Send tickets to AI for normalization
    # ---------------------------------------------------------
    normalized = await normalize_tickets(tickets)

    # ---------------------------------------------------------
    # 2. Convert AI response into database format
    #
    # AI format:
    # {
    #     "id": "...",
    #     "description": "..."
    # }
    #
    # Database format:
    # {
    #     "ticket_id": "...",
    #     "description": "..."
    # }
    # ---------------------------------------------------------
    normalized_tickets = [
        {
            "ticket_id": ticket["id"],
            "description": ticket["description"],
        }
        for ticket in normalized
    ]

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

    return (
        db.query(TicketNormalization)
        .filter(TicketNormalization.workspace_id == workspace_id)
        .order_by(TicketNormalization.created_at.desc())
        .first()
    )


def delete_normalizations(
    db: Session,
    workspace_id: UUID,
) -> int:

    records = (
        db.query(TicketNormalization)
        .filter(TicketNormalization.workspace_id == workspace_id)
        .all()
    )

    if not records:
        return 0

    for record in records:
        db.delete(record)

    db.commit()

    return len(records)
