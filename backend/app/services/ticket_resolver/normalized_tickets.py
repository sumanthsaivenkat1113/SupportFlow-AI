# ----------------------------------------------------------------------------------
# app/services/ticket_resolver/normalized_tickets.py
# ----------------------------------------------------------------------------------
"""Load normalized tickets for a workspace."""

import uuid

from sqlalchemy.orm import Session

from app.services.ticket_normaliser import get_normalization


def load_normalized_tickets(
    db: Session, workspace_id: uuid.UUID
) -> list[dict[str, str]]:
    normalization = get_normalization(db, workspace_id)
    if not normalization:
        return []

    normalized = normalization.normalized_tickets or []
    return [
        {
            "ticket_id": str(item["ticket_id"]).strip(),
            "description": item["description"],
        }
        for item in normalized
    ]
