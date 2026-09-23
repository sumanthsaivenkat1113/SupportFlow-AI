# ----------------------------------------------------------------------------------
# app/services/ticket_resolver/raw_ticket_map.py
# ----------------------------------------------------------------------------------
"""Build the external-ticket-id → UUID mapping for a workspace."""

import logging
import uuid

from sqlalchemy.orm import Session

from app.models import Ticket
from app.services.ticket_resolver.payload_utils import (
    BODY_KEYS,
    CUSTOMER_ID_KEYS,
    PAYLOAD_ATTRS,
    TICKET_NUMBER_KEYS,
    coerce_payload,
    first_key,
)

logger = logging.getLogger(__name__)


def load_raw_ticket_map(db: Session, workspace_id: uuid.UUID) -> dict[str, dict]:
    """
    Return {external_ticket_number: {"uuid": UUID, "customer_id": str|None, "body": str}}
    e.g. {"F1-1001": {"uuid": "21c3...", "customer_id": "CUST-3001", "body": "..."}}
    """
    tickets = db.query(Ticket).filter(Ticket.workspace_id == workspace_id).all()

    logger.info(
        "[ticket_resolver] workspace=%s → %d tickets from DB",
        workspace_id,
        len(tickets),
    )

    if not tickets:
        total = db.query(Ticket).count()
        logger.warning(
            "[ticket_resolver] NO tickets for workspace %s. Total tickets in DB: %d",
            workspace_id,
            total,
        )
        return {}

    sample = tickets[0]
    attrs = [a for a in vars(sample).keys() if not a.startswith("_")]
    logger.info("[ticket_resolver] First ticket attrs: %s", attrs)

    mapping: dict[str, dict] = {}

    for t in tickets:
        payload = None
        for attr in PAYLOAD_ATTRS:
            payload = coerce_payload(getattr(t, attr, None))
            if payload:
                break

        if not payload:
            logger.debug(
                "[ticket_resolver] ticket %s: no JSON payload found on attrs %s",
                t.id,
                PAYLOAD_ATTRS,
            )
            continue

        ext_id_raw = first_key(payload, TICKET_NUMBER_KEYS)
        if not ext_id_raw:
            logger.debug(
                "[ticket_resolver] ticket %s: no ticket-number key in payload (keys=%s)",
                t.id,
                list(payload.keys())[:12],
            )
            continue

        ext_id = str(ext_id_raw).strip()
        customer_id = first_key(payload, CUSTOMER_ID_KEYS)
        customer_id = str(customer_id).strip() if customer_id else None
        body = first_key(payload, BODY_KEYS) or ""

        mapping[ext_id] = {
            "uuid": t.id,
            "customer_id": customer_id,
            "body": body,
        }

    logger.info(
        "[ticket_resolver] built map with %d entries. Sample: %s",
        len(mapping),
        list(mapping.keys())[:5],
    )
    return mapping
