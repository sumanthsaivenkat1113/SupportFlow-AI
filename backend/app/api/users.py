from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import CurrentClerkId
from app.core.database import get_db
from app.services.user_service import create_or_sync_user

router = APIRouter(
    prefix="/api/users",
    tags=["Users"],
)


@router.get("/me")
def get_me(
    clerk_id: CurrentClerkId,
    db: Session = Depends(get_db),
):
    user = create_or_sync_user(
        db=db,
        clerk_id=clerk_id,
    )

    return {
        "id": str(user.id),
        "clerk_id": user.clerk_id,
        "name": user.name,
        "email": user.email,
        "img_url": user.img_url,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
    }
