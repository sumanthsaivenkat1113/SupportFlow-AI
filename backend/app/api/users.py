from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import CurrentClerkId
from app.core.database import get_db
from app.services.user_service import create_or_sync_user
from app.schemas.user import UserResponse

router = APIRouter(
    prefix="/api/users",
    tags=["Users"],
)


@router.get("/me", response_model=UserResponse)
def get_me(
    clerk_id: CurrentClerkId,
    db: Session = Depends(get_db),
):
    user = create_or_sync_user(
        db=db,
        clerk_id=clerk_id,
    )

    return user
