# ----------------------------------------------------------------------------------
# app/services/tickets_export.py
# ----------------------------------------------------------------------------------
"""Ticket resolution export service."""

import csv
import io
import json
import uuid
from typing import Literal

from openpyxl import Workbook
from sqlalchemy.orm import Session

from app.models import Ticket, TicketResolution

GeneratedType = Literal["ai-automated", "human-required"]


def get_workspace_ticket_export_data(
    db: Session,
    workspace_id: uuid.UUID,
    generated: GeneratedType | None = None,
) -> list[dict]:
    """
    Get ticket resolutions for a workspace.

    Args:
        db: SQLAlchemy database session.
        workspace_id: Workspace UUID.
        generated:
        - "ai-automated" -> only automatically resolved tickets
        - "human-required" -> only tickets requiring human review
        - None -> all tickets

    Returns:
        List of exportable ticket resolution records.
    """

    query = (
        db.query(Ticket, TicketResolution)
        .join(
            TicketResolution,
            Ticket.id == TicketResolution.ticket_id,
        )
        .filter(
            Ticket.workspace_id == workspace_id,
        )
    )

    # ------------------------------------------------------------
    # # Filter by resolution outcome when requested
    # ------------------------------------------------------------

    if generated is not None:
        query = query.filter(TicketResolution.generated == generated)

    rows = query.order_by(TicketResolution.created_at.desc()).all()

    data: list[dict] = []

    for ticket, resolution in rows:
        customer_ticket = ticket.customer_ticket or {}

        data.append(
            {
                "ticket_id": str(ticket.id),
                "external_ticket_id": customer_ticket.get("ticket_id"),
                "subject": customer_ticket.get("subject"),
                "customer": customer_ticket.get("customer"),
                "description": customer_ticket.get("description"),
                "response": resolution.response,
                "generated": resolution.generated,
                "model_name": resolution.model_name,
                "status": resolution.status,
                "created_at": (
                    resolution.created_at.isoformat() if resolution.created_at else None
                ),
            }
        )

    return data


# ----------------------------------------------------------------------------------
# JSON
# ----------------------------------------------------------------------------------


def generate_json_export(
    data: list[dict],
) -> tuple[io.BytesIO, str]:
    """Generate JSON export."""

    payload = json.dumps(
        data,
        indent=2,
        ensure_ascii=False,
    )

    buffer = io.BytesIO(payload.encode("utf-8"))

    buffer.seek(0)

    return (
        buffer,
        "application/json",
    )


# ----------------------------------------------------------------------------------
# CSV
# ----------------------------------------------------------------------------------


def generate_csv_export(
    data: list[dict],
) -> tuple[io.StringIO, str]:
    """Generate CSV export."""

    buffer = io.StringIO()

    if not data:
        buffer.write("No records found\n")
        buffer.seek(0)

        return (
            buffer,
            "text/csv",
        )

    fieldnames = list(data[0].keys())

    writer = csv.DictWriter(
        buffer,
        fieldnames=fieldnames,
    )

    writer.writeheader()
    writer.writerows(data)

    buffer.seek(0)

    return (
        buffer,
        "text/csv",
    )


# ----------------------------------------------------------------------------------
# Excel
# ----------------------------------------------------------------------------------


def generate_excel_export(
    data: list[dict],
) -> tuple[io.BytesIO, str]:
    """Generate Excel XLSX export."""

    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Ticket Resolutions"

    if not data:
        worksheet.append(["No records found"])

    else:
        fieldnames = list(data[0].keys())

        # Header
        worksheet.append(fieldnames)

        # Rows
        for row in data:
            worksheet.append([row.get(field) for field in fieldnames])

    # Basic column sizing
    for column in worksheet.columns:
        max_length = 0

        column_letter = column[0].column_letter

        for cell in column:
            value = "" if cell.value is None else str(cell.value)

            max_length = max(
                max_length,
                len(value),
            )

        worksheet.column_dimensions[column_letter].width = min(max_length + 2, 50)

    buffer = io.BytesIO()

    workbook.save(buffer)

    buffer.seek(0)

    return (
        buffer,
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
