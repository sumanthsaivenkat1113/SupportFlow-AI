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
    """
    Resolve one normalized ticket.

    Flow:
        normalized ticket
            ↓
        retrieve top-k chunks
            ↓
        prepare context
            ↓
        generate AI resolution
            ↓
        return resolution + generated classification
    """

    ticket_id = normalized_ticket["ticket_id"]
    description = normalized_ticket["description"]

    raw = raw_ticket_map.get(ticket_id, {})
    external_customer_id = raw.get("customer_id")

    # ------------------------------------------------------------------
    # Retrieve relevant knowledge-base chunks
    # ------------------------------------------------------------------

    chunks = top_k_chunks(
        all_chunks,
        chunk_matrix,
        query_embedding,
        top_k,
    )

    context = prepare_context(chunks)

    # ------------------------------------------------------------------
    # Generate resolution
    # ------------------------------------------------------------------

    try:
        result = await generate_resolution(
            ticket_id=ticket_id,
            external_customer_id=external_customer_id,
            question=description,
            context=context,
            semaphore=semaphore,
        )

    except Exception as e:
        logger.exception(
            "[ticket_resolver] LLM failed for %s",
            ticket_id,
        )

        # No generated classification is available if the LLM failed.
        return {
            "ticket_id": ticket_id,
            "external_customer_id": external_customer_id,
            "ticket_resolution": None,
            "context": context,
            "model_name": None,
            "generated": None,
            "error": str(e),
        }

    # ------------------------------------------------------------------
    # Successful resolution
    #
    # generate_resolution() already returns:
    #
    #   generated = "ai-automated"
    #   OR
    #   generated = "human-required"
    #
    # Return the complete result so persistence.py can save it.
    # ------------------------------------------------------------------

    return {
        "ticket_id": result["ticket_id"],
        "external_customer_id": result.get("external_customer_id"),
        "ticket_resolution": result.get("ticket_resolution"),
        "context": result.get("context"),
        "model_name": result.get("model_name"),
        "generated": result.get("generated"),
        "error": result.get("error"),
        "_timing": result.get("_timing"),
    }
