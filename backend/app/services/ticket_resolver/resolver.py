# ----------------------------------------------------------------------------------
# app/services/ticket_resolver/resolver.py
# ----------------------------------------------------------------------------------
"""Resolve a single normalized ticket via retrieval + LLM."""

import asyncio
import logging
from typing import Any

import numpy as np

from app.ai.ticket_resolver import generate_resolution
from app.models import DocumentChunk
from app.services.ticket_resolver.retrieval import prepare_context, top_k_chunks

logger = logging.getLogger(__name__)


async def resolve_one(
    normalized_ticket: dict[str, str],
    query_embedding: list[float],
    raw_ticket_map: dict[str, dict],
    all_chunks: list[DocumentChunk],
    chunk_matrix: "np.ndarray | None",
    top_k: int,
    semaphore: asyncio.Semaphore,
) -> dict[str, Any]:
    ticket_id = normalized_ticket["ticket_id"]
    description = normalized_ticket["description"]

    raw = raw_ticket_map.get(ticket_id, {})
    external_customer_id = raw.get("customer_id")

    chunks = top_k_chunks(all_chunks, chunk_matrix, query_embedding, top_k)
    context = prepare_context(chunks)

    try:
        result = await generate_resolution(
            ticket_id=ticket_id,
            external_customer_id=external_customer_id,
            question=description,
            context=context,
            semaphore=semaphore,
        )
    except Exception as e:
        logger.exception("[ticket_resolver] LLM failed for %s", ticket_id)
        return {
            "ticket_id": ticket_id,
            "external_customer_id": external_customer_id,
            "ticket_resolution": None,
            "context": context,
            "error": str(e),
        }

    return result
