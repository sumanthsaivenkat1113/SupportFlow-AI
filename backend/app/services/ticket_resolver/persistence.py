# ----------------------------------------------------------------------------------
# app/services/ticket_resolver/persistence.py
# ----------------------------------------------------------------------------------
"""Persist ticket resolutions and build the response payload."""

import logging
import uuid
from typing import Any

from sqlalchemy.orm import Session

from app.models import TicketResolution

logger = logging.getLogger(__name__)


VALID_GENERATED_VALUES = {
    "ai-automated",
    "human-required",
}


def persist_resolutions(
    db: Session,
    all_results: list[dict[str, Any]],
    raw_ticket_map: dict[str, dict],
) -> list[dict[str, Any]]:
    """Map external ticket IDs to UUIDs and persist resolutions."""

    persisted: list[dict[str, Any]] = []
    inserted = 0

    for r in all_results:
        external_id = r["ticket_id"]

        raw = raw_ticket_map.get(external_id)

        if not raw:
            persisted.append(
                {
                    "ticket_id": external_id,
                    "ticket_uuid": None,
                    "response": r.get("ticket_resolution"),
                    "generated": r.get("generated"),
                    "error": (
                        "No matching ticket row found. "
                        f"Map has {len(raw_ticket_map)} entries; "
                        f"sample keys: {list(raw_ticket_map.keys())[:5]}"
                    ),
                }
            )
            continue

        ticket_uuid: uuid.UUID = raw["uuid"]

        generated = r.get("generated")

        if generated not in VALID_GENERATED_VALUES:
            logger.error(
                "[ticket_resolver] Invalid generated value for %s: %r",
                external_id,
                generated,
            )

            # A failed/invalid AI classification should never be treated
            # as automatically resolvable.
            generated = "human-required"

        row = TicketResolution(
            ticket_id=ticket_uuid,
            response=r.get("ticket_resolution") or "",
            context=r.get("context"),
            model_name=r.get("model_name"),
            status="generated",
            generated=generated,
        )

        db.add(row)
        inserted += 1

        persisted.append(
            {
                "ticket_id": external_id,
                "ticket_uuid": str(ticket_uuid),
                "response": row.response,
                "context": row.context,
                "model_name": row.model_name,
                "status": row.status,
                "generated": row.generated,
                "error": r.get("error"),
                "timing": r.get("_timing"),
            }
        )

    if inserted:
        db.commit()
    else:
        db.rollback()

    return persisted
