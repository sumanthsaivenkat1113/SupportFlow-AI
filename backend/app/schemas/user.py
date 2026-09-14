import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UserResponse(BaseModel):
    id: uuid.UUID
    clerk_id: str
    name: str | None
    email: str
    img_url: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
