from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from ai.ticket_normaliser import normalize_tickets as ai_normalize_tickets
from models.ticket_normaliser import TicketNormalization


async def create_normalization(
    db: AsyncSession,
    workspace_id: UUID,
    tickets: list[dict],
) -> TicketNormalization:
    # Normalize tickets using AI
    normalized = await ai_normalize_tickets(tickets)

    record = TicketNormalization(
        workspace_id=workspace_id,
        normalized_tickets=normalized,
    )

    db.add(record)
    await db.commit()
    await db.refresh(record)

    return record


async def get_normalization(
    db: AsyncSession,
    workspace_id: UUID,
) -> TicketNormalization | None:
    stmt = (
        select(TicketNormalization)
        .where(TicketNormalization.workspace_id == workspace_id)
        .order_by(TicketNormalization.created_at.desc())
        .limit(1)
    )

    result = await db.execute(stmt)

    return result.scalar_one_or_none()


async def delete_normalizations(
    db: AsyncSession,
    workspace_id: UUID,
) -> int:
    stmt = delete(TicketNormalization).where(
        TicketNormalization.workspace_id == workspace_id
    )

    result = await db.execute(stmt)
    await db.commit()

    return result.rowcount or 0
