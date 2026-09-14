import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class WorkspaceResponse(BaseModel):
    id: uuid.UUID
    owner_id: uuid.UUID
    name: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WorkspaceDocumentResponse(BaseModel):
    pdf_no: int
    pdf_file_name: str


class WorkspaceCreateResponse(BaseModel):
    success: bool
    message: str
    workspace_name: str
    pdf_files: list[WorkspaceDocumentResponse]
    total_pdf_files: int
