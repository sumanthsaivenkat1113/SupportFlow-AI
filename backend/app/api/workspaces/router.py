import time

from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.api.workspaces.deps import CurrentUser, OwnedWorkspace
from app.core.database import get_db
from app.schemas.workspace import (
    ChunkingStrategy,
    WorkspaceCreateResponse,
)
from app.services import workspace_service

from . import documents
from . import tickets as tickets_router

router = APIRouter(
    prefix="/api/workspaces",
    tags=["Workspaces"],
)


# ============================================================
# POST /api/workspaces
# ============================================================


@router.post("", response_model=WorkspaceCreateResponse)
async def create_workspace(
    user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
    workspace_name: Annotated[str, Form(...)],
    pdf_files: Annotated[list[UploadFile], File(...)],
    chunking_strategy: Annotated[ChunkingStrategy, Form()] = ChunkingStrategy.SEMANTIC,
):
    start_time = time.perf_counter()

    response = await workspace_service.create_workspace_with_files(
        db=db,
        user_id=user.id,
        workspace_name=workspace_name,
        pdf_files=pdf_files,
        chunking_strategy=chunking_strategy,
    )

    response.time_execution = round(
        (time.perf_counter() - start_time),
        2,
    )

    return response


# ============================================================
# GET /api/workspaces
# ============================================================


@router.get("")
def get_workspaces(
    user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
):
    return workspace_service.list_workspaces_for_user(db=db, user_id=user.id)


# ============================================================
# GET /api/workspaces/{workspace_id}
# ============================================================


@router.get("/{workspace_id}")
def get_workspace(
    workspace: OwnedWorkspace,
    db: Annotated[Session, Depends(get_db)],
):
    return workspace_service.get_workspace_details(db=db, workspace=workspace)


# ============================================================
# DELETE /api/workspaces/{workspace_id}
# ============================================================


@router.delete("/{workspace_id}")
def delete_workspace(
    workspace: OwnedWorkspace,
    db: Annotated[Session, Depends(get_db)],
):
    return workspace_service.delete_workspace_and_children(db=db, workspace=workspace)


# ============================================================
# GET /api/workspaces/{workspace_id}/status
# ============================================================


@router.get("/{workspace_id}/status")
def get_workspace_status(
    workspace: OwnedWorkspace,
    db: Annotated[Session, Depends(get_db)],
):
    return workspace_service.get_workspace_status(db=db, workspace=workspace)


# ============================================================
# Sub-routers
# ============================================================

# Document routes: /api/workspaces/{workspace_id}/documents
router.include_router(documents.router)

router.include_router(tickets_router.router)
