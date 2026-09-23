# ----------------------------------------------------------------------------------
# app/services/ticket_resolver/orchestrator.py
# ----------------------------------------------------------------------------------
"""Batch orchestration for resolving all normalized tickets in a workspace."""

import asyncio
import logging
import time
import uuid
from typing import Any

from sqlalchemy.orm import Session

from app.services.embeddings import embed_texts
from app.services.ticket_resolver.normalized_tickets import load_normalized_tickets
from app.services.ticket_resolver.persistence import persist_resolutions
from app.services.ticket_resolver.raw_ticket_map import load_raw_ticket_map
from app.services.ticket_resolver.resolver import resolve_one
from app.services.ticket_resolver.retrieval import load_workspace_chunks

logger = logging.getLogger(__name__)


async def resolve_workspace_tickets(
    db: Session,
    workspace_id: uuid.UUID,
    batch_size: int = 5,
    top_k: int = 3,
) -> dict[str, Any]:
    wall_start = time.perf_counter()

    normalized = load_normalized_tickets(db, workspace_id)
    if not normalized:
        return {
            "success": False,
            "workspace_id": workspace_id,
            "total_tickets": 0,
            "total_batches": 0,
            "batch_size": batch_size,
            "resolutions": [],
            "time_execution": 0.0,
        }

    raw_ticket_map = load_raw_ticket_map(db, workspace_id)
    if not raw_ticket_map:
        logger.error(
            "[ticket_resolver] raw_ticket_map is EMPTY for workspace %s. "
            "Check that Ticket.customer_ticket holds the JSON payload and "
            "Ticket.workspace_id matches.",
            workspace_id,
        )

    # Load all workspace chunks ONCE instead of per-ticket.
    all_chunks, chunk_matrix = load_workspace_chunks(db, workspace_id)

    descriptions = [t["description"] for t in normalized]
    embeddings = await embed_texts(descriptions)

    batches = [
        list(zip(normalized[i : i + batch_size], embeddings[i : i + batch_size]))
        for i in range(0, len(normalized), batch_size)
    ]

    semaphore = asyncio.Semaphore(min(max(batch_size, 1), 10))

    all_results: list[dict[str, Any]] = []
    for batch_idx, batch in enumerate(batches):
        logger.info(
            "[ticket_resolver] processing batch %d/%d (%d tickets)",
            batch_idx + 1,
            len(batches),
            len(batch),
        )
        tasks = [
            resolve_one(
                normalized_ticket=item[0],
                query_embedding=item[1],
                raw_ticket_map=raw_ticket_map,
                all_chunks=all_chunks,
                chunk_matrix=chunk_matrix,
                top_k=top_k,
                semaphore=semaphore,
            )
            for item in batch
        ]
        batch_results = await asyncio.gather(*tasks, return_exceptions=False)
        all_results.extend(batch_results)

    persisted = persist_resolutions(db, all_results, raw_ticket_map)

    return {
        "success": True,
        "workspace_id": workspace_id,
        "total_tickets": len(normalized),
        "total_batches": len(batches),
        "batch_size": batch_size,
        "resolutions": persisted,
        "time_execution": round(time.perf_counter() - wall_start, 3),
    }
