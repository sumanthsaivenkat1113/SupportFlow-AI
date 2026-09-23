import asyncio
import time
import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.ticket_resolver import generate_resolution
from app.models import DocumentChunk, Ticket, TicketResolution
from app.services.embeddings import embed_texts
from app.services.ticket_normaliser import get_normalization


# ------------------------------------------------------------------
# 1. Load normalized tickets + raw-ticket map
# ------------------------------------------------------------------
def _load_raw_ticket_map(db: Session, workspace_id: uuid.UUID) -> dict[str, dict]:
    """
    Returns {external_ticket_number: {"uuid": ..., "customer_id": ..., "body": ...}}
    e.g. {"F3-3001": {"uuid": "21c3...", "customer_id": "CUST-3001", "body": "..."}}
    """
    tickets = db.query(Ticket).filter(Ticket.workspace_id == workspace_id).all()

    mapping: dict[str, dict] = {}
    for t in tickets:
        payload = t.customer_ticket or {}
        ext_id = payload.get("ticket__number")
        if not ext_id:
            continue
        mapping[ext_id] = {
            "uuid": t.id,
            "customer_id": payload.get("customer__id"),
            "body": payload.get("details__body") or "",
            "subject": payload.get("ticket__subject") or "",
        }
    return mapping


def load_normalized_tickets(
    db: Session, workspace_id: uuid.UUID
) -> list[dict[str, str]]:
    """
    Returns normalized tickets for a workspace:
    [{"ticket_id": "F3-3001", "description": "..."}]
    """
    normalization = get_normalization(db, workspace_id)
    if not normalization:
        return []

    normalized = normalization.normalized_tickets or []
    return [
        {
            "ticket_id": item["ticket_id"],
            "description": item["description"],
        }
        for item in normalized
    ]


# ------------------------------------------------------------------
# 2. Retrieval
# ------------------------------------------------------------------
def retrieve_chunks(
    db: Session,
    workspace_id: uuid.UUID,
    query_embedding: list[float],
    top_k: int = 3,
) -> list[DocumentChunk]:
    """
    Workspace-scoped vector search. Uses pgvector cosine distance.
    """
    statement = (
        select(DocumentChunk)
        .where(DocumentChunk.workspace_id == workspace_id)
        .order_by(DocumentChunk.embedding.cosine_distance(query_embedding))
        .limit(top_k)
    )
    return list(db.scalars(statement).all())


def prepare_context(chunks: list[DocumentChunk]) -> str:
    """
    Join retrieved chunks into a single context string.
    """
    if not chunks:
        return ""
    return "\n\n---\n\n".join(chunk.content for chunk in chunks)


# ------------------------------------------------------------------
# 3. Embed all normalized descriptions (single batch call)
# ------------------------------------------------------------------
async def _embed_descriptions(descriptions: list[str]) -> list[list[float]]:
    if not descriptions:
        return []
    return await embed_texts(descriptions)


# ------------------------------------------------------------------
# 4. Resolve one ticket (embed → retrieve → prepare → generate)
# ------------------------------------------------------------------
async def _resolve_one(
    db: Session,
    workspace_id: uuid.UUID,
    normalized_ticket: dict[str, str],
    query_embedding: list[float],
    raw_ticket_map: dict[str, dict],
    top_k: int,
) -> dict[str, Any]:
    ticket_id = normalized_ticket["ticket_id"]
    description = normalized_ticket["description"]

    raw = raw_ticket_map.get(ticket_id, {})
    external_customer_id = raw.get("customer_id")

    # 3. Retrieve relevant chunks
    chunks = retrieve_chunks(
        db=db,
        workspace_id=workspace_id,
        query_embedding=query_embedding,
        top_k=top_k,
    )

    # 4. Prepare context
    context = prepare_context(chunks)

    # 5. Generate resolution
    try:
        result = await generate_resolution(
            ticket_id=ticket_id,
            external_customer_id=external_customer_id,
            question=description,
            context=context,
        )
    except Exception as e:
        return {
            "ticket_id": ticket_id,
            "external_customer_id": external_customer_id,
            "ticket_resolution": None,
            "context": context,
            "error": str(e),
        }

    return result


# ------------------------------------------------------------------
# 5. Batch orchestration
# ------------------------------------------------------------------
async def resolve_workspace_tickets(
    db: Session,
    workspace_id: uuid.UUID,
    batch_size: int = 5,
    top_k: int = 3,
) -> dict[str, Any]:
    """
    End-to-end pipeline:
      normalized tickets → embeddings → retrieval → context → LLM
      → persisted ticket_resolutions (with UUID ticket_id)
    """
    wall_start = time.perf_counter()

    # --- Load ---
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

    raw_ticket_map = _load_raw_ticket_map(db, workspace_id)

    # --- Embeddings (single batched call) ---
    descriptions = [t["description"] for t in normalized]
    embeddings = await _embed_descriptions(descriptions)

    # --- Batches of N ---
    batches = [
        list(zip(normalized[i : i + batch_size], embeddings[i : i + batch_size]))
        for i in range(0, len(normalized), batch_size)
    ]

    all_results: list[dict[str, Any]] = []

    # --- Process batch by batch ---
    for batch_idx, batch in enumerate(batches):
        tasks = [
            _resolve_one(
                db=db,
                workspace_id=workspace_id,
                normalized_ticket=item[0],
                query_embedding=item[1],
                raw_ticket_map=raw_ticket_map,
                top_k=top_k,
            )
            for item in batch
        ]
        batch_results = await asyncio.gather(*tasks, return_exceptions=False)
        all_results.extend(batch_results)

    # --- Transform external id → UUID and persist ---
    persisted: list[dict[str, Any]] = []
    for r in all_results:
        external_id = r["ticket_id"]
        raw = raw_ticket_map.get(external_id)

        if not raw:
            # No matching ticket row → skip persistence
            persisted.append(
                {
                    "ticket_id": external_id,
                    "ticket_uuid": None,
                    "response": r.get("ticket_resolution"),
                    "error": "No matching ticket row found",
                }
            )
            continue

        ticket_uuid: uuid.UUID = raw["uuid"]

        row = TicketResolution(
            ticket_id=ticket_uuid,
            response=r.get("ticket_resolution") or "",
            context=r.get("context"),
            model_name=r.get("model_name"),
            status="generated",
        )
        db.add(row)

        persisted.append(
            {
                "ticket_id": external_id,  # F3-3001 (original)
                "ticket_uuid": str(ticket_uuid),  # 21c30991-... (transformed)
                "response": row.response,
                "context": row.context,
                "model_name": row.model_name,
                "status": row.status,
                "error": r.get("error"),
                "timing": r.get("_timing"),
            }
        )

    db.commit()

    return {
        "success": True,
        "workspace_id": workspace_id,
        "total_tickets": len(normalized),
        "total_batches": len(batches),
        "batch_size": batch_size,
        "resolutions": persisted,
        "time_execution": round(time.perf_counter() - wall_start, 3),
    }
