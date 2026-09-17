# app/services/ticket_classifier.py

import asyncio
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.ai.ticket_classifier import classify_tickets
from app.models.tickets import Ticket
from app.models.ticket_classification import TicketClassification
from app.models.ticket_classification_item import TicketClassificationItem
from app.models.workspaces import Workspace
from app.services.exceptions import NotFoundError, ValidationError
from app.services.ticket_normaliser import get_normalization

# ============================================================
# CONFIGURATION
# ============================================================

MODEL_NAME = "qwen/qwen3.8-27b"


# ============================================================
# DTOs
# ============================================================


@dataclass
class ClassifiedTicket:
    ticket_id: UUID
    classification: str
    confidence: float
    reason: str


@dataclass
class ClassificationDetail:
    classification_id: UUID
    total_tickets: int
    tickets: list[ClassifiedTicket]


@dataclass
class ClassificationSummary:
    classification_id: UUID
    model_name: str | None
    created_at: datetime
    total_tickets: int
    automatable_count: int
    human_review_count: int


@dataclass
class GlobalClassifiedTicket:
    ticket_id: UUID
    classification: str
    confidence: float
    reason: str


@dataclass
class GlobalClassification:
    classification_id: UUID
    workspace_id: UUID
    workspace_name: str
    model_name: str | None
    created_at: datetime
    total_tickets: int
    tickets: list[GlobalClassifiedTicket]


# ============================================================
# INTERNAL HELPERS
# ============================================================


def _require_workspace(
    db: Session,
    workspace_id: UUID,
) -> Workspace:

    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()

    if workspace is None:
        raise NotFoundError("Workspace not found.")

    return workspace


def _to_detail(
    record: TicketClassification,
) -> ClassificationDetail:

    tickets = [
        ClassifiedTicket(
            ticket_id=item.ticket_id,
            classification=item.classification,
            confidence=(float(item.confidence) if item.confidence is not None else 0.0),
            reason=item.reason or "",
        )
        for item in record.items
    ]

    return ClassificationDetail(
        classification_id=record.id,
        total_tickets=len(tickets),
        tickets=tickets,
    )


def _build_ticket_id_map(
    db: Session,
    workspace_id: UUID,
) -> dict[str, UUID]:
    """
    Build a mapping between the external/customer ticket ID
    used by normalization/classification and the internal
    database ticket UUID used by ticket_classification_items.

    Example:

        customer_ticket.ticket_id
            4e55c93f-5205-4847-926d-53ea4424fceb

                    ↓

        tickets.id
            28edff1f-58b2-45ed-b050-fd31657a9a9d
    """

    tickets = db.query(Ticket).filter(Ticket.workspace_id == workspace_id).all()

    ticket_id_map: dict[str, UUID] = {}

    for ticket in tickets:

        customer_ticket = ticket.customer_ticket

        if not customer_ticket:
            continue

        customer_ticket_id = customer_ticket.get("ticket_id")

        if not customer_ticket_id:
            continue

        customer_ticket_id = str(customer_ticket_id)

        ticket_id_map[customer_ticket_id] = ticket.id

    return ticket_id_map


def _validate_ticket_mapping(
    classified: list[dict],
    ticket_id_map: dict[str, UUID],
) -> None:
    """
    Make sure every ticket returned by the classifier exists
    in the workspace's tickets table.
    """

    missing_ticket_ids: list[str] = []

    for result in classified:

        customer_ticket_id = str(result["ticket_id"])

        if customer_ticket_id not in ticket_id_map:
            missing_ticket_ids.append(customer_ticket_id)

    if missing_ticket_ids:

        preview = ", ".join(missing_ticket_ids[:5])

        if len(missing_ticket_ids) > 5:
            preview += ", ..."

        raise ValidationError(
            "Some classified tickets could not be mapped "
            f"to database tickets: {preview}"
        )


# ============================================================
# CREATE
# ============================================================


async def create_classification(
    db: Session,
    workspace_id: UUID,
) -> ClassificationDetail:

    # --------------------------------------------------------
    # 1. Verify workspace exists
    # --------------------------------------------------------

    _require_workspace(
        db=db,
        workspace_id=workspace_id,
    )

    # --------------------------------------------------------
    # 2. Get latest normalization
    # --------------------------------------------------------

    normalization = get_normalization(
        db=db,
        workspace_id=workspace_id,
    )

    if normalization is None:
        raise ValidationError("No normalization found for this workspace.")

    normalized_tickets = normalization.normalized_tickets

    if not normalized_tickets:
        raise ValidationError("No normalized tickets found for this workspace.")

    # --------------------------------------------------------
    # 3. Classify all tickets in ONE Groq request
    # --------------------------------------------------------

    try:

        classified = await asyncio.to_thread(
            classify_tickets,
            normalized_tickets,
        )

    except ValueError as exc:

        # AI output/input validation failures → 400
        raise ValidationError(str(exc)) from exc

    if not classified:
        raise ValidationError("No tickets were classified.")

    # --------------------------------------------------------
    # 4. Build customer ticket ID → database ticket ID map
    # --------------------------------------------------------
    #
    # IMPORTANT:
    #
    # AI returns:
    #
    #   customer_ticket.ticket_id
    #
    # But TicketClassificationItem.ticket_id is an FK to:
    #
    #   tickets.id
    #
    # Therefore we MUST translate the ID before inserting.
    # --------------------------------------------------------

    ticket_id_map = _build_ticket_id_map(
        db=db,
        workspace_id=workspace_id,
    )

    if not ticket_id_map:
        raise ValidationError("No imported tickets found for this workspace.")

    # --------------------------------------------------------
    # 5. Validate all AI results can be mapped
    # --------------------------------------------------------

    _validate_ticket_mapping(
        classified=classified,
        ticket_id_map=ticket_id_map,
    )

    # --------------------------------------------------------
    # 6. Persist parent + items in one transaction
    # --------------------------------------------------------

    try:

        record = TicketClassification(
            workspace_id=workspace_id,
            model_name=MODEL_NAME,
        )

        db.add(record)

        # Generate UUID for parent before creating children.
        db.flush()

        for result in classified:

            customer_ticket_id = str(result["ticket_id"])

            # ------------------------------------------------
            # IMPORTANT:
            #
            # Use the INTERNAL database ticket UUID here.
            #
            # Do NOT use:
            #     UUID(result["ticket_id"])
            #
            # because that is the customer/external ticket ID.
            # ------------------------------------------------

            database_ticket_id = ticket_id_map[customer_ticket_id]

            db.add(
                TicketClassificationItem(
                    classification_id=record.id,
                    ticket_id=database_ticket_id,
                    classification=result["classification"],
                    confidence=result["confidence"],
                    reason=result["reason"],
                )
            )

        db.commit()

    except Exception:

        db.rollback()
        raise

    # --------------------------------------------------------
    # 7. Refresh + return DTO
    # --------------------------------------------------------

    db.refresh(record)

    return _to_detail(record)


# ============================================================
# LIST (per workspace)
# ============================================================


def list_classifications(
    db: Session,
    workspace_id: UUID,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[ClassificationSummary], int]:

    # --------------------------------------------------------
    # 1. Verify workspace exists
    # --------------------------------------------------------

    _require_workspace(
        db,
        workspace_id,
    )

    # --------------------------------------------------------
    # 2. Query classification runs
    # --------------------------------------------------------

    base_query = db.query(TicketClassification).filter(
        TicketClassification.workspace_id == workspace_id,
    )

    total = base_query.count()

    records = (
        base_query.order_by(TicketClassification.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    # --------------------------------------------------------
    # 3. Aggregate item counts
    # --------------------------------------------------------

    counts: dict[UUID, dict[str, int]] = {}

    if records:

        ids = [record.id for record in records]

        rows = (
            db.query(
                TicketClassificationItem.classification_id,
                func.count(TicketClassificationItem.id).label("total"),
                func.sum(
                    case(
                        (
                            TicketClassificationItem.classification == "automatable",
                            1,
                        ),
                        else_=0,
                    )
                ).label("automatable"),
                func.sum(
                    case(
                        (
                            TicketClassificationItem.classification == "human_review",
                            1,
                        ),
                        else_=0,
                    )
                ).label("human_review"),
            )
            .filter(TicketClassificationItem.classification_id.in_(ids))
            .group_by(TicketClassificationItem.classification_id)
            .all()
        )

        for (
            classification_id,
            item_total,
            automatable,
            human_review,
        ) in rows:

            counts[classification_id] = {
                "total": int(item_total),
                "automatable": int(automatable or 0),
                "human_review": int(human_review or 0),
            }

    # --------------------------------------------------------
    # 4. Build summaries
    # --------------------------------------------------------

    summaries: list[ClassificationSummary] = []

    for record in records:

        stats = counts.get(
            record.id,
            {
                "total": 0,
                "automatable": 0,
                "human_review": 0,
            },
        )

        summaries.append(
            ClassificationSummary(
                classification_id=record.id,
                model_name=record.model_name,
                created_at=record.created_at,
                total_tickets=stats["total"],
                automatable_count=stats["automatable"],
                human_review_count=stats["human_review"],
            )
        )

    return summaries, total


# ============================================================
# LIST ALL (across all workspaces)
# ============================================================


def list_all_classifications(
    db: Session,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[GlobalClassification], int]:

    # --------------------------------------------------------
    # 1. Query classification runs joined with workspace
    # --------------------------------------------------------

    base_query = db.query(
        TicketClassification,
        Workspace,
    ).join(
        Workspace,
        Workspace.id == TicketClassification.workspace_id,
    )

    total = base_query.count()

    rows = (
        base_query.order_by(TicketClassification.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    # --------------------------------------------------------
    # 2. Build DTOs
    # --------------------------------------------------------

    results: list[GlobalClassification] = []

    for record, workspace in rows:

        tickets = [
            GlobalClassifiedTicket(
                ticket_id=item.ticket_id,
                classification=item.classification,
                confidence=(
                    float(item.confidence) if item.confidence is not None else 0.0
                ),
                reason=item.reason or "",
            )
            for item in record.items
        ]

        results.append(
            GlobalClassification(
                classification_id=record.id,
                workspace_id=workspace.id,
                workspace_name=workspace.name,
                model_name=record.model_name,
                created_at=record.created_at,
                total_tickets=len(tickets),
                tickets=tickets,
            )
        )

    return results, total


# ============================================================
# GET ONE
# ============================================================


def get_classification(
    db: Session,
    workspace_id: UUID,
    classification_id: UUID,
) -> ClassificationDetail:

    # --------------------------------------------------------
    # 1. Verify workspace exists
    # --------------------------------------------------------

    _require_workspace(
        db,
        workspace_id,
    )

    # --------------------------------------------------------
    # 2. Find classification
    # --------------------------------------------------------

    record = (
        db.query(TicketClassification)
        .filter(
            TicketClassification.id == classification_id,
            TicketClassification.workspace_id == workspace_id,
        )
        .first()
    )

    if record is None:
        raise NotFoundError("Classification not found.")

    # --------------------------------------------------------
    # 3. Return DTO
    # --------------------------------------------------------

    return _to_detail(record)
