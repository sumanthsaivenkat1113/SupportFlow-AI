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
    # 1. Build AI input.
    #
    # Ticket source schemas vary wildly (100+ possible shapes:
    # flat fields, nested "details.body", Jira-style "fields.*",
    # arbitrary custom exports, etc). Rather than hardcoding
    # every possible field path in Python, we hand the AI the
    # raw, untouched ticket JSON and let it locate the human
    # ticket id and the issue/description text itself.
    #
    # The one thing we DO need to guarantee ourselves is a safe
    # join key so we can validate the AI's response 1:1 against
    # what we sent. Business ticket ids ("F1-1001", "CUST-3001",
    # Jira "key", etc.) are not reliable for that — they differ
    # in shape and aren't guaranteed present. The database row's
    # own id IS always a real, unique UUID, so we use that as the
    # internal join key and let ticket_id be AI-extracted content.
    # ---------------------------------------------------------

    ai_input: list[dict] = []

    for row in tickets:

        internal_id = row.get("id")
        raw_ticket = row.get("customer_ticket") or {}

        if not internal_id:
            raise ValueError("Ticket row is missing its internal id.")

        if not raw_ticket:
            raise ValueError(f"Ticket row {internal_id} has no ticket data.")

        ai_input.append(
            {
                "internal_id": str(internal_id),
                "raw_ticket": raw_ticket,
            }
        )

    if not ai_input:
        raise ValueError("No tickets provided for normalization.")

    # ---------------------------------------------------------
    # 2. Send raw tickets to AI for schema-agnostic extraction.
    #
    # normalize_tickets is synchronous (Groq client is sync),
    # so we push it to a worker thread to avoid blocking the
    # event loop.
    # ---------------------------------------------------------

    normalized = await asyncio.to_thread(normalize_tickets, ai_input)

    if not normalized:
        raise ValueError("AI returned no normalized tickets.")

    # ---------------------------------------------------------
    # 3. Map AI output → database format.
    #
    # normalize_tickets already validated internal_id coverage
    # (no missing/duplicate/unknown rows) and guarantees a
    # non-empty ticket_id (falling back to internal_id) and a
    # non-empty description. We just reshape for storage here.
    # ---------------------------------------------------------

    normalized_tickets: list[dict] = []

    for item in normalized:
        normalized_tickets.append(
            {
                "ticket_id": item["ticket_id"],
                "description": item["description"],
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
