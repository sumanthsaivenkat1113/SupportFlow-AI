import json
from typing import Any

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.models.ticket_imports import TicketImport
from app.models.tickets import Ticket
from app.models.workspaces import Workspace
from app.services.tickets_normalization import (
    csv_to_json,
    excel_to_json,
    json_to_json,
)

MAX_TICKETS_PER_FILE = 20

# MIME types we accept and how to route them
_SUPPORTED_TYPES: dict[str, str] = {
    "application/json": "json",
    "application/vnd.ms-excel": "excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "excel",
    "text/csv": "csv",
    "application/csv": "csv",
}

_EXTENSION_MAP: dict[str, str] = {
    "json": "json",
    "xlsx": "excel",
    "xlsm": "excel",
    "xls": "excel",
    "csv": "csv",
}


def _detect_file_kind(upload: UploadFile) -> str:
    """Return one of 'json', 'excel', 'csv' or raise 400."""
    if upload.content_type in _SUPPORTED_TYPES:
        return _SUPPORTED_TYPES[upload.content_type]

    if upload.filename:
        ext = upload.filename.rsplit(".", 1)[-1].lower()
        if ext in _EXTENSION_MAP:
            return _EXTENSION_MAP[ext]

    raise HTTPException(
        status_code=400,
        detail=(
            f"Unsupported file type for {upload.filename or 'file'}. "
            "Allowed: .json, .xlsx, .xls, .csv"
        ),
    )


def _normalize(kind: str, file_bytes: bytes) -> list[dict[str, Any]]:
    try:
        if kind == "json":
            return json_to_json(file_bytes)
        if kind == "excel":
            return excel_to_json(file_bytes)
        if kind == "csv":
            return csv_to_json(file_bytes)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    raise HTTPException(status_code=400, detail="Unsupported file type")


async def create_ticket_import(
    *,
    db: Session,
    workspace: Workspace,
    upload: UploadFile,
) -> dict:
    """Import one JSON/Excel/CSV file into the workspace."""

    if not upload.filename:
        raise HTTPException(status_code=400, detail="File must have a filename")

    file_bytes = await upload.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    kind = _detect_file_kind(upload)
    records = _normalize(kind, file_bytes)

    if not records:
        raise HTTPException(
            status_code=400,
            detail="No ticket records found in the file",
        )

    if len(records) > MAX_TICKETS_PER_FILE:
        raise HTTPException(
            status_code=400,
            detail=(
                f"File contains {len(records)} records; "
                f"maximum is {MAX_TICKETS_PER_FILE}"
            ),
        )

    # Create the import row first (status=processing)
    ticket_import = TicketImport(
        workspace_id=workspace.id,
        file_name=upload.filename,
        file_type=kind,
        status="processing",
        total_tickets=len(records),
    )
    db.add(ticket_import)
    db.flush()

    processed = 0
    failed = 0
    error_messages: list[str] = []

    try:
        for index, record in enumerate(records):
            try:
                # Ensure record is JSON-serializable
                normalized = json.loads(json.dumps(record, default=str))
                db.add(
                    Ticket(
                        workspace_id=workspace.id,
                        import_id=ticket_import.id,
                        customer_ticket=normalized,
                    )
                )
                processed += 1
            except Exception as exc:  # noqa: BLE001 — per-row isolation
                failed += 1
                error_messages.append(f"row {index + 1}: {exc}")

        ticket_import.processed_tickets = processed
        ticket_import.failed_tickets = failed

        if processed == 0:
            ticket_import.status = "failed"
            ticket_import.error_message = "; ".join(error_messages[:5])
        elif failed > 0:
            ticket_import.status = "completed"
            ticket_import.error_message = f"{failed} row(s) failed: " + "; ".join(
                error_messages[:5]
            )
        else:
            ticket_import.status = "completed"

        db.commit()

    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to import tickets",
        ) from exc

    return {
        "success": True,
        "message": "Tickets imported successfully",
        "import_id": ticket_import.id,
        "workspace_id": workspace.id,
        "file_name": ticket_import.file_name,
        "file_type": ticket_import.file_type,
        "status": ticket_import.status,
        "total_tickets": ticket_import.total_tickets,
        "processed_tickets": ticket_import.processed_tickets,
        "failed_tickets": ticket_import.failed_tickets,
    }


def get_ticket_import_details(*, db: Session, ticket_import: TicketImport) -> dict:
    tickets = (
        db.query(Ticket)
        .filter(Ticket.import_id == ticket_import.id)
        .order_by(Ticket.created_at.asc())
        .all()
    )

    return {
        "success": True,
        "import": {
            "id": ticket_import.id,
            "workspace_id": ticket_import.workspace_id,
            "file_name": ticket_import.file_name,
            "file_type": ticket_import.file_type,
            "status": ticket_import.status,
            "total_tickets": ticket_import.total_tickets,
            "processed_tickets": ticket_import.processed_tickets,
            "failed_tickets": ticket_import.failed_tickets,
            "error_message": ticket_import.error_message,
            "created_at": ticket_import.created_at,
            "updated_at": ticket_import.updated_at,
        },
        "tickets": [
            {
                "id": t.id,
                "workspace_id": t.workspace_id,
                "import_id": t.import_id,
                "customer_ticket": t.customer_ticket,
                "created_at": t.created_at,
                "updated_at": t.updated_at,
            }
            for t in tickets
        ],
        "total_tickets": len(tickets),
    }


def get_ticket_import_status(*, ticket_import: TicketImport) -> dict:
    return {
        "success": True,
        "import_id": ticket_import.id,
        "status": ticket_import.status,
        "progress": {
            "total": ticket_import.total_tickets,
            "processed": ticket_import.processed_tickets,
            "failed": ticket_import.failed_tickets,
        },
        "error_message": ticket_import.error_message,
    }


def list_tickets_for_workspace(
    *,
    db: Session,
    workspace: Workspace,
    limit: int = 50,
    offset: int = 0,
) -> dict:
    base = db.query(Ticket).filter(Ticket.workspace_id == workspace.id)

    total = base.count()
    tickets = base.order_by(Ticket.created_at.asc()).offset(offset).limit(limit).all()

    return {
        "success": True,
        "workspace_id": workspace.id,
        "total_tickets": total,
        "tickets": [
            {
                "id": t.id,
                "workspace_id": t.workspace_id,
                "import_id": t.import_id,
                "customer_ticket": t.customer_ticket,
                "created_at": t.created_at,
                "updated_at": t.updated_at,
            }
            for t in tickets
        ],
    }


def get_ticket_details(*, ticket: Ticket) -> dict:
    return {
        "success": True,
        "ticket": {
            "id": ticket.id,
            "workspace_id": ticket.workspace_id,
            "import_id": ticket.import_id,
            "customer_ticket": ticket.customer_ticket,
            "created_at": ticket.created_at,
            "updated_at": ticket.updated_at,
        },
    }


def delete_ticket(*, db: Session, ticket: Ticket) -> dict:
    workspace_id = ticket.workspace_id
    ticket_id = ticket.id

    try:
        db.delete(ticket)
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to delete ticket",
        ) from exc

    return {
        "success": True,
        "message": "Ticket deleted successfully",
        "workspace_id": workspace_id,
        "ticket_id": ticket_id,
    }
