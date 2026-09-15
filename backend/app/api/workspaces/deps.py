from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import CurrentClerkId
from app.core.database import get_db
from app.models.workspaces import Workspace
from app.services.user_service import create_or_sync_user
from app.models.documents import Document


def get_current_user(
    clerk_id: CurrentClerkId,
    db: Annotated[Session, Depends(get_db)],
):
    """Resolve (or create) the local user for the authenticated clerk_id."""
    return create_or_sync_user(db=db, clerk_id=clerk_id)


CurrentUser = Annotated[object, Depends(get_current_user)]


def get_owned_workspace(
    workspace_id: UUID,
    user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> Workspace:
    """Fetch a workspace by id, ensuring it belongs to the current user."""
    workspace = (
        db.query(Workspace)
        .filter(
            Workspace.id == workspace_id,
            Workspace.owner_id == user.id,
        )
        .first()
    )

    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    return workspace


OwnedWorkspace = Annotated[Workspace, Depends(get_owned_workspace)]

from app.models.documents import Document


def get_owned_document(
    document_id: UUID,
    workspace: OwnedWorkspace,
    db: Annotated[Session, Depends(get_db)],
) -> Document:
    """Fetch a document by id, ensuring it belongs to the owned workspace."""
    document = (
        db.query(Document)
        .filter(
            Document.id == document_id,
            Document.workspace_id == workspace.id,
        )
        .first()
    )

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    return document


OwnedDocument = Annotated[Document, Depends(get_owned_document)]
