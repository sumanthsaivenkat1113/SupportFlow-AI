from enum import Enum
import uuid
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ChunkingStrategy(str, Enum):
    SEMANTIC = "Semantic"
    TOKEN_BASED_500 = "token_based_500"
    STRUCTURE_AWARE = "Structure_aware"


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
    workspace_id: UUID
    workspace_name: str
    pdf_files: list[WorkspaceDocumentResponse]
    total_pdf_files: int
    chunking_strategy: ChunkingStrategy
    no_of_chunks: int
    time_execution: float | None = None
