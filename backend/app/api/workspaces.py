from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
)
from sqlalchemy.orm import Session

from app.core.auth import CurrentClerkId
from app.core.database import get_db

from app.models.documents import Document
from app.models.document_chunks import DocumentChunk
from app.models.workspaces import Workspace

from app.schemas.workspace import (
    ChunkingStrategy,
    WorkspaceCreateResponse,
    WorkspaceDocumentResponse,
)

from app.services.chunking_service import create_document_chunks
from app.services.embeddings import embed_texts
from app.services.pdf_to_text_service import extract_text_from_pdf
from app.services.user_service import create_or_sync_user

router = APIRouter(
    prefix="/api/workspaces",
    tags=["Workspaces"],
)


@router.post(
    "",
    response_model=WorkspaceCreateResponse,
)
async def create_workspace(
    clerk_id: CurrentClerkId,
    db: Annotated[Session, Depends(get_db)],
    workspace_name: Annotated[str, Form(...)],
    pdf_files: Annotated[list[UploadFile], File(...)],
    chunking_strategy: Annotated[
        ChunkingStrategy,
        Form(),
    ] = ChunkingStrategy.SEMANTIC,
):
    # ------------------------------------------------------------
    # Validate workspace name
    # ------------------------------------------------------------

    workspace_name = workspace_name.strip()

    if not workspace_name:
        raise HTTPException(
            status_code=400,
            detail="Workspace name is required",
        )

    # ------------------------------------------------------------
    # Validate PDF count
    # ------------------------------------------------------------

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

    # ------------------------------------------------------------
    # Get / sync authenticated user
    # ------------------------------------------------------------

    user = create_or_sync_user(
        db=db,
        clerk_id=clerk_id,
    )

    # ------------------------------------------------------------
    # Validate uploaded files
    # ------------------------------------------------------------

    for pdf_file in pdf_files:

        if not pdf_file.filename:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file must have a filename",
            )

        if pdf_file.content_type != "application/pdf":
            raise HTTPException(
                status_code=400,
                detail=f"{pdf_file.filename} is not a PDF file",
            )

    # ------------------------------------------------------------
    # Create workspace
    # ------------------------------------------------------------

    workspace = Workspace(
        owner_id=user.id,
        name=workspace_name,
    )

    db.add(workspace)
    db.flush()

    response_files: list[WorkspaceDocumentResponse] = []

    total_chunk_count = 0

    try:
        # --------------------------------------------------------
        # Process uploaded PDFs
        # --------------------------------------------------------

        for index, pdf_file in enumerate(pdf_files, start=1):

            # ----------------------------------------------------
            # Read PDF
            # ----------------------------------------------------

            file_bytes = await pdf_file.read()

            if not file_bytes:
                raise HTTPException(
                    status_code=400,
                    detail=f"{pdf_file.filename} is empty",
                )

            # ----------------------------------------------------
            # Extract PDF text
            # ----------------------------------------------------

            try:
                extracted_text = extract_text_from_pdf(file_bytes)

            except Exception as exc:
                raise HTTPException(
                    status_code=400,
                    detail=(f"Failed to extract text from " f"{pdf_file.filename}"),
                ) from exc

            if not extracted_text:
                raise HTTPException(
                    status_code=400,
                    detail=(f"No text could be extracted from " f"{pdf_file.filename}"),
                )

            # ----------------------------------------------------
            # Create document
            # ----------------------------------------------------

            document = Document(
                workspace_id=workspace.id,
                file_name=pdf_file.filename,
                extracted_text=extracted_text,
                status="processing",
            )

            db.add(document)
            db.flush()

            # ----------------------------------------------------
            # Create chunks
            # ----------------------------------------------------

            try:
                chunks = await create_document_chunks(
                    text=extracted_text,
                    strategy=chunking_strategy.value,
                )

            except Exception as exc:
                raise HTTPException(
                    status_code=500,
                    detail=(f"Failed to create chunks for " f"{pdf_file.filename}"),
                ) from exc

            if not chunks:
                raise HTTPException(
                    status_code=400,
                    detail=(f"No chunks could be created from " f"{pdf_file.filename}"),
                )

            # ----------------------------------------------------
            # Generate embeddings
            # ----------------------------------------------------

            try:
                embeddings = await embed_texts(chunks)

            except Exception as exc:
                raise HTTPException(
                    status_code=500,
                    detail=(
                        f"Failed to generate embeddings for " f"{pdf_file.filename}"
                    ),
                ) from exc

            if len(chunks) != len(embeddings):
                raise HTTPException(
                    status_code=500,
                    detail=(
                        f"Chunk and embedding count mismatch "
                        f"for {pdf_file.filename}"
                    ),
                )

            # ----------------------------------------------------
            # Save document chunks
            # ----------------------------------------------------

            for chunk_index, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                document_chunk = DocumentChunk(
                    document_id=document.id,
                    workspace_id=workspace.id,
                    chunk_index=chunk_index,
                    content=chunk,
                    token_count=len(chunk.split()),
                    embedding=embedding,
                    metadata={
                        "chunking_strategy": (chunking_strategy.value),
                    },
                )

                db.add(document_chunk)

            # ----------------------------------------------------
            # Update document status
            # ----------------------------------------------------

            document.status = "completed"

            # ----------------------------------------------------
            # Count chunks
            # ----------------------------------------------------

            total_chunk_count += len(chunks)

            # ----------------------------------------------------
            # Add PDF to response
            # ----------------------------------------------------

            response_files.append(
                WorkspaceDocumentResponse(
                    pdf_no=index,
                    pdf_file_name=pdf_file.filename,
                )
            )

            # ----------------------------------------------------
            # Close uploaded file
            # ----------------------------------------------------

            await pdf_file.close()

        # --------------------------------------------------------
        # Commit everything
        # --------------------------------------------------------

        db.commit()

    except HTTPException:
        db.rollback()

        for pdf_file in pdf_files:
            await pdf_file.close()

        raise

    except Exception as exc:
        db.rollback()

        for pdf_file in pdf_files:
            await pdf_file.close()

        raise HTTPException(
            status_code=500,
            detail="Failed to create workspace",
        ) from exc

    # ------------------------------------------------------------
    # Response
    # ------------------------------------------------------------

    return WorkspaceCreateResponse(
        success=True,
        message="workspace successfully created",
        workspace_name=workspace.name,
        pdf_files=response_files,
        total_pdf_files=len(response_files),
        chunking_strategy=chunking_strategy.value,
        no_of_chunks=total_chunk_count,
    )
