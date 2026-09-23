# ----------------------------------------------------------------------------------
# app/services/ticket_resolver/retrieval.py
# ----------------------------------------------------------------------------------
"""Workspace-scoped document-chunk retrieval (in-memory kNN)."""

import uuid

import numpy as np
from sqlalchemy.orm import Session

from app.models import DocumentChunk


def load_workspace_chunks(
    db: Session, workspace_id: uuid.UUID
) -> tuple[list[DocumentChunk], "np.ndarray | None"]:
    """Load all workspace chunks once; pre-normalize embeddings for cosine kNN."""
    chunks = (
        db.query(DocumentChunk).filter(DocumentChunk.workspace_id == workspace_id).all()
    )
    if not chunks:
        return [], None

    matrix = np.asarray([c.embedding for c in chunks], dtype=np.float32)
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms[norms == 0] = 1e-8
    matrix = matrix / norms
    return chunks, matrix


def top_k_chunks(
    chunks: list[DocumentChunk],
    matrix: "np.ndarray | None",
    query_embedding: list[float],
    top_k: int,
) -> list[DocumentChunk]:
    if matrix is None or not chunks:
        return []
    q = np.asarray(query_embedding, dtype=np.float32)
    qn = np.linalg.norm(q) or 1e-8
    q = q / qn
    sims = matrix @ q
    top_idx = np.argsort(-sims)[:top_k]
    return [chunks[i] for i in top_idx]


def prepare_context(chunks: list[DocumentChunk]) -> str:
    if not chunks:
        return ""
    return "\n\n---\n\n".join(chunk.content for chunk in chunks)
