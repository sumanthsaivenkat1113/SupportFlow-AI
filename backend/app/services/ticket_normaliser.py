# app/services/ticket_normaliser.py

import asyncio
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.ticket_normaliser import TicketNormalization

from app.ai.ticket_normaliser import normalize_tickets

# ============================================================
# CREATE
# ============================================================


async def create_normalization(
    db: Session,
    workspace_id: UUID,
    tickets: list[dict],
) -> TicketNormalization:

    # ---------------------------------------------------------
    # 1. Flatten nested customer_ticket into AI-friendly input
    # ---------------------------------------------------------

    ai_input: list[dict] = []

    for row in tickets:

        customer = row.get("customer_ticket") or {}

        ticket_id = customer.get("ticket_id") or row.get("id")
        description = (customer.get("description") or "").strip()

        if not ticket_id:
            raise ValueError(f"Ticket row {row.get('id')} has no customer ticket id.")

        if not description:
            raise ValueError(f"Ticket {ticket_id} has an empty description.")

        ai_input.append(
            {
                "ticket_id": str(ticket_id),
                "description": description,
            }
        )

    if not ai_input:
        raise ValueError("No tickets provided for normalization.")

    # ---------------------------------------------------------
    # 2. Send flat tickets to AI
    #
    # normalize_tickets is synchronous (Groq client is sync),
    # so we push it to a worker thread to avoid blocking the
    # event loop.
    # ---------------------------------------------------------

    normalized = await asyncio.to_thread(normalize_tickets, ai_input)

    if not normalized:
        raise ValueError("AI returned no normalized tickets.")

    # ---------------------------------------------------------
    # 3. Map AI output → database format
    # ---------------------------------------------------------

    normalized_tickets: list[dict] = []

    for item in normalized:

        ticket_id = item.get("ticket_id") or item.get("id")
        description = (item.get("description") or "").strip()

        if not ticket_id:
            raise ValueError(f"AI returned an item without a ticket id: {item}")

        if not description:
            raise ValueError(
                f"AI returned an empty description for ticket {ticket_id}."
            )

        normalized_tickets.append(
            {
                "ticket_id": str(ticket_id),
                "description": description,
            }
        )

    # ---------------------------------------------------------
    # 4. Persist
    # ---------------------------------------------------------

    record = TicketNormalization(
        workspace_id=workspace_id,
        normalized_tickets=normalized_tickets,
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return record


# ============================================================
# GET
# ============================================================


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


# ============================================================
# DELETE
# ============================================================


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
