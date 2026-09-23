# ----------------------------------------------------------------------------------
# app/services/ticket_resolver/listing.py
# ----------------------------------------------------------------------------------
"""Read path: list persisted ticket resolutions for a workspace."""

import uuid

from sqlalchemy.orm import Session

from app.models import Ticket, TicketResolution


def list_workspace_ticket_resolutions(
    db: Session, workspace_id: uuid.UUID
) -> list[TicketResolution]:
    return (
        db.query(TicketResolution)
        .join(Ticket, Ticket.id == TicketResolution.ticket_id)
        .filter(Ticket.workspace_id == workspace_id)
        .order_by(TicketResolution.created_at.desc())
        .all()
    )
