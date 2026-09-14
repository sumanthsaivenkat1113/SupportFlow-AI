from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.auth import CurrentClerkId
from app.core.database import get_db
from app.schemas.workspace import (
    WorkspaceCreateResponse,
    WorkspaceDocumentResponse,
)
from app.services.pdf_to_text_service import extract_text_from_pdf
from app.services.user_service import create_or_sync_user
from app.models.documents import Document
from app.models.workspaces import Workspace

router = APIRouter(
    prefix="/api/workspaces",
    tags=["Workspaces"],
)


@router.post(
    "",
    response_model=WorkspaceCreateResponse,
)
async def create_workspace(
    workspace_name: str = Form(...),
    pdf_files: list[UploadFile] = File(...),
    clerk_id: CurrentClerkId = None,
    db: Session = Depends(get_db),
):
    # --------------------------------------------------
    # Validate workspace name
    # --------------------------------------------------

    workspace_name = workspace_name.strip()

    if not workspace_name:
        raise HTTPException(
            status_code=400,
            detail="Workspace name is required",
        )

    # --------------------------------------------------
    # Validate PDF count
    # --------------------------------------------------

    if not pdf_files:
        raise HTTPException(
            status_code=400,
            detail="At least one PDF file is required",
        )

    if len(pdf_files) > 5:
        raise HTTPException(
            status_code=400,
            detail="You can upload a maximum of 5 PDF files",
        )

    # --------------------------------------------------
    # Get authenticated user
    # --------------------------------------------------

    user = create_or_sync_user(
        db=db,
        clerk_id=clerk_id,
    )

    # --------------------------------------------------
    # Validate files
    # --------------------------------------------------

    for pdf_file in pdf_files:
        if pdf_file.content_type != "application/pdf":
            raise HTTPException(
                status_code=400,
                detail=f"{pdf_file.filename} is not a PDF file",
            )

    # --------------------------------------------------
    # Create workspace
    # --------------------------------------------------

    workspace = Workspace(
        owner_id=user.id,
        name=workspace_name,
    )

    db.add(workspace)
    db.flush()

    # --------------------------------------------------
    # Process PDFs
    # --------------------------------------------------

    response_files = []

    for index, pdf_file in enumerate(pdf_files, start=1):
        file_bytes = await pdf_file.read()

        try:
            extracted_text = extract_text_from_pdf(file_bytes)
        except Exception:
            db.rollback()

            raise HTTPException(
                status_code=400,
                detail=f"Failed to extract text from {pdf_file.filename}",
            )

        document = Document(
            workspace_id=workspace.id,
            file_name=pdf_file.filename or f"document-{index}.pdf",
            extracted_text=extracted_text,
            status="completed",
        )

        db.add(document)

        response_files.append(
            WorkspaceDocumentResponse(
                pdf_no=index,
                pdf_file_name=pdf_file.filename or f"document-{index}.pdf",
            )
        )

    # --------------------------------------------------
    # Commit everything
    # --------------------------------------------------

    db.commit()

    return WorkspaceCreateResponse(
        success=True,
        message="workspace successfully created",
        workspace_name=workspace.name,
        pdf_files=response_files,
        total_pdf_files=len(response_files),
    )
