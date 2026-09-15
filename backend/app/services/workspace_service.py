from uuid import UUID

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

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

MAX_PDF_FILES = 5


# ============================================================
# Validation helpers
# ============================================================


def _validate_workspace_name(name: str) -> str:
    name = name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Workspace name is required")
    return name


def _validate_pdf_files(pdf_files: list[UploadFile]) -> None:
    if not pdf_files:
        raise HTTPException(
            status_code=400,
            detail="At least one PDF file is required",
        )

    if len(pdf_files) > MAX_PDF_FILES:
        raise HTTPException(
            status_code=400,
            detail=f"You can upload a maximum of {MAX_PDF_FILES} PDF files",
        )

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


# ============================================================
# Per-file pipeline
# ============================================================


async def _process_pdf(
    *,
    db: Session,
    workspace: Workspace,
    pdf_file: UploadFile,
    index: int,
    chunking_strategy: ChunkingStrategy,
) -> tuple[WorkspaceDocumentResponse, int]:
    """Extract → chunk → embed → persist a single PDF. Returns (response, chunk_count)."""

    file_bytes = await pdf_file.read()

    if not file_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"{pdf_file.filename} is empty",
        )

    # -------- Extract text --------
    try:
        extracted_text = extract_text_from_pdf(file_bytes)
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to extract text from {pdf_file.filename}",
        ) from exc

    if not extracted_text:
        raise HTTPException(
            status_code=400,
            detail=f"No text could be extracted from {pdf_file.filename}",
        )

    # -------- Persist document --------
    document = Document(
        workspace_id=workspace.id,
        file_name=pdf_file.filename,
        extracted_text=extracted_text,
        status="processing",
    )
    db.add(document)
    db.flush()

    # -------- Chunk --------
    try:
        chunks = await create_document_chunks(
            text=extracted_text,
            strategy=chunking_strategy.value,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create chunks for {pdf_file.filename}",
        ) from exc

    if not chunks:
        raise HTTPException(
            status_code=400,
            detail=f"No chunks could be created from {pdf_file.filename}",
        )

    # -------- Embed --------
    try:
        embeddings = await embed_texts(chunks)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate embeddings for {pdf_file.filename}",
        ) from exc

    if len(chunks) != len(embeddings):
        raise HTTPException(
            status_code=500,
            detail=f"Chunk and embedding count mismatch for {pdf_file.filename}",
        )

    # -------- Persist chunks --------
    for chunk_index, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        db.add(
            DocumentChunk(
                document_id=document.id,
                workspace_id=workspace.id,
                chunk_index=chunk_index,
                content=chunk,
                token_count=len(chunk.split()),
                embedding=embedding,
                metadata={"chunking_strategy": chunking_strategy.value},
            )
        )

    document.status = "completed"

    return (
        WorkspaceDocumentResponse(
            pdf_no=index,
            pdf_file_name=pdf_file.filename,
        ),
        len(chunks),
    )


# ============================================================
# Workspace public service API
# ============================================================


async def create_workspace_with_files(
    *,
    db: Session,
    user_id,
    workspace_name: str,
    pdf_files: list[UploadFile],
    chunking_strategy: ChunkingStrategy,
) -> WorkspaceCreateResponse:

    workspace_name = _validate_workspace_name(workspace_name)
    _validate_pdf_files(pdf_files)

    workspace = Workspace(owner_id=user_id, name=workspace_name)
    db.add(workspace)
    db.flush()

    response_files: list[WorkspaceDocumentResponse] = []
    total_chunk_count = 0

    try:
        for index, pdf_file in enumerate(pdf_files, start=1):
            doc_response, chunk_count = await _process_pdf(
                db=db,
                workspace=workspace,
                pdf_file=pdf_file,
                index=index,
                chunking_strategy=chunking_strategy,
            )
            response_files.append(doc_response)
            total_chunk_count += chunk_count
            await pdf_file.close()

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

    return WorkspaceCreateResponse(
        success=True,
        message="workspace successfully created",
        workspace_name=workspace.name,
        pdf_files=response_files,
        total_pdf_files=len(response_files),
        chunking_strategy=chunking_strategy.value,
        no_of_chunks=total_chunk_count,
    )


def list_workspaces_for_user(*, db: Session, user_id) -> dict:
    workspaces = (
        db.query(Workspace)
        .filter(Workspace.owner_id == user_id)
        .order_by(Workspace.created_at.desc())
        .all()
    )

    response = []
    for workspace in workspaces:
        documents = (
            db.query(Document).filter(Document.workspace_id == workspace.id).all()
        )
        total_chunks = (
            db.query(DocumentChunk)
            .filter(DocumentChunk.workspace_id == workspace.id)
            .count()
        )
        response.append(
            {
                "id": str(workspace.id),
                "name": workspace.name,
                "created_at": workspace.created_at,
                "updated_at": workspace.updated_at,
                "total_documents": len(documents),
                "total_chunks": total_chunks,
                "documents": [
                    {
                        "id": str(d.id),
                        "file_name": d.file_name,
                        "status": d.status,
                    }
                    for d in documents
                ],
            }
        )

    return {
        "success": True,
        "total_workspaces": len(response),
        "workspaces": response,
    }


def get_workspace_details(*, db: Session, workspace: Workspace) -> dict:
    documents = (
        db.query(Document)
        .filter(Document.workspace_id == workspace.id)
        .order_by(Document.created_at.asc())
        .all()
    )

    document_response = []
    total_chunks = 0

    for document in documents:
        chunk_count = (
            db.query(DocumentChunk)
            .filter(DocumentChunk.document_id == document.id)
            .count()
        )
        total_chunks += chunk_count
        document_response.append(
            {
                "id": str(document.id),
                "file_name": document.file_name,
                "status": document.status,
                "chunk_count": chunk_count,
                "created_at": document.created_at,
                "updated_at": document.updated_at,
            }
        )

    return {
        "success": True,
        "workspace": {
            "id": str(workspace.id),
            "name": workspace.name,
            "created_at": workspace.created_at,
            "updated_at": workspace.updated_at,
        },
        "documents": document_response,
        "total_documents": len(document_response),
        "total_chunks": total_chunks,
    }


def delete_workspace_and_children(*, db: Session, workspace: Workspace) -> dict:
    try:
        document_ids = [
            d.id
            for d in db.query(Document)
            .filter(Document.workspace_id == workspace.id)
            .all()
        ]

        if document_ids:
            db.query(DocumentChunk).filter(
                DocumentChunk.document_id.in_(document_ids)
            ).delete(synchronize_session=False)

        db.query(Document).filter(Document.workspace_id == workspace.id).delete(
            synchronize_session=False
        )

        workspace_id = workspace.id
        db.delete(workspace)
        db.commit()

    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to delete workspace",
        ) from exc

    return {
        "success": True,
        "message": "Workspace deleted successfully",
        "workspace_id": str(workspace_id),
    }


def get_workspace_status(*, db: Session, workspace: Workspace) -> dict:
    documents = (
        db.query(Document)
        .filter(Document.workspace_id == workspace.id)
        .order_by(Document.created_at.asc())
        .all()
    )

    total_documents = len(documents)
    completed_documents = sum(1 for d in documents if d.status == "completed")
    processing_documents = sum(1 for d in documents if d.status == "processing")
    failed_documents = sum(1 for d in documents if d.status == "failed")

    if total_documents == 0:
        overall_status = "empty"
    elif failed_documents > 0:
        overall_status = "failed"
    elif completed_documents == total_documents:
        overall_status = "completed"
    else:
        overall_status = "processing"

    return {
        "success": True,
        "workspace_id": str(workspace.id),
        "workspace_name": workspace.name,
        "status": overall_status,
        "progress": {
            "total_documents": total_documents,
            "completed": completed_documents,
            "processing": processing_documents,
            "failed": failed_documents,
        },
        "documents": [
            {
                "id": str(d.id),
                "file_name": d.file_name,
                "status": d.status,
            }
            for d in documents
        ],
    }


# ============================================================
# Document public service API
# ============================================================


def list_documents_for_workspace(*, db: Session, workspace: Workspace) -> dict:
    """Return all documents in a workspace, each with its chunk count."""

    documents = (
        db.query(Document)
        .filter(Document.workspace_id == workspace.id)
        .order_by(Document.created_at.asc())
        .all()
    )

    document_response = []
    for document in documents:
        chunk_count = (
            db.query(DocumentChunk)
            .filter(DocumentChunk.document_id == document.id)
            .count()
        )
        document_response.append(
            {
                "id": document.id,
                "workspace_id": document.workspace_id,
                "file_name": document.file_name,
                "status": document.status,
                "chunk_count": chunk_count,
                "created_at": document.created_at,
                "updated_at": document.updated_at,
            }
        )

    return {
        "success": True,
        "workspace_id": workspace.id,
        "workspace_name": workspace.name,
        "total_documents": len(document_response),
        "documents": document_response,
    }


def delete_document_from_workspace(
    *,
    db: Session,
    workspace: Workspace,
    document: Document,
) -> dict:
    """Delete a document and all of its chunks."""

    document_id = document.id
    workspace_id = workspace.id

    try:
        # 1. Delete chunks for this document
        db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id).delete(
            synchronize_session=False
        )

        # 2. Delete the document itself
        db.delete(document)

        db.commit()

    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to delete document",
        ) from exc

    return {
        "success": True,
        "message": "Document deleted successfully",
        "workspace_id": workspace_id,
        "document_id": document_id,
    }
