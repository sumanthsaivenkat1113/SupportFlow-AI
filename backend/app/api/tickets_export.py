# ----------------------------------------------------------------------------------
# app/api/tickets_export.py
# ----------------------------------------------------------------------------------

import uuid
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.tickets_export import (
    generate_csv_export,
    generate_excel_export,
    generate_json_export,
    get_workspace_ticket_export_data,
)

router = APIRouter(
    prefix="/api/workspaces",
    tags=["Ticket Export"],
)


@router.get("/{workspace_id}/ticket-resolutions/export")
def export_workspace_ticket_resolutions(
    workspace_id: uuid.UUID,
    generated: Literal["ai-automated", "human-required"],
    format: Literal["json", "csv", "excel"] = "json",
    db: Session = Depends(get_db),
):
    """
    Export ticket resolutions for a workspace filtered by generated type.

    generated:
        - ai-automated
        - human-required

    format:
        - json
        - csv
        - excel
    """

    data = get_workspace_ticket_export_data(
        db=db,
        workspace_id=workspace_id,
        generated=generated,
    )

    if not data:
        raise HTTPException(
            status_code=404,
            detail=(
                f"No '{generated}' ticket resolutions found " "for this workspace."
            ),
        )

    if format == "json":
        buffer, media_type = generate_json_export(data)
        filename = f"workspace_{workspace_id}_{generated}_ticket_resolutions.json"

    elif format == "csv":
        buffer, media_type = generate_csv_export(data)
        filename = f"workspace_{workspace_id}_{generated}_ticket_resolutions.csv"

    elif format == "excel":
        buffer, media_type = generate_excel_export(data)
        filename = f"workspace_{workspace_id}_{generated}_ticket_resolutions.xlsx"

    else:
        raise HTTPException(
            status_code=400,
            detail="Unsupported export format.",
        )

    return StreamingResponse(
        buffer,
        media_type=media_type,
        headers={"Content-Disposition": (f'attachment; filename="{filename}"')},
    )
