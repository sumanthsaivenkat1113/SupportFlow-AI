from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class DocumentSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workspace_id: UUID
    file_name: str
    status: str
    chunk_count: int
    created_at: datetime
    updated_at: datetime


class DocumentListResponse(BaseModel):
    success: bool
    workspace_id: UUID
    workspace_name: str
    total_documents: int
    documents: list[DocumentSummary]


class DocumentDeleteResponse(BaseModel):
    success: bool
    message: str
    workspace_id: UUID
    document_id: UUID
