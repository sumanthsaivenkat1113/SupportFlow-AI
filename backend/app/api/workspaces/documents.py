from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.workspaces.deps import OwnedDocument, OwnedWorkspace
from app.core.database import get_db
from app.schemas.document import (
    DocumentDeleteResponse,
    DocumentListResponse,
)
from app.services import workspace_service

router = APIRouter()


# ============================================================
# GET /api/workspaces/{workspace_id}/documents
# ============================================================


@router.get(
    "/{workspace_id}/documents",
    response_model=DocumentListResponse,
)
def list_documents(
    workspace: OwnedWorkspace,
    db: Annotated[Session, Depends(get_db)],
):
    """
    List all documents belonging to the workspace.
    """
    return workspace_service.list_documents_for_workspace(
        db=db,
        workspace=workspace,
    )


# ============================================================
# DELETE /api/workspaces/{workspace_id}/documents/{document_id}
# ============================================================


@router.delete(
    "/{workspace_id}/documents/{document_id}",
    response_model=DocumentDeleteResponse,
)
def delete_document(
    workspace: OwnedWorkspace,
    document: OwnedDocument,
    db: Annotated[Session, Depends(get_db)],
):
    """
    Delete a single document and all its chunks.
    """
    return workspace_service.delete_document_from_workspace(
        db=db,
        workspace=workspace,
        document=document,
    )
