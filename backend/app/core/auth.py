from typing import Annotated

from fastapi import Depends, HTTPException, Request
from clerk_backend_api import (
    AuthenticateRequestOptions,
    authenticate_request,
)

from app.core.config import settings


def get_current_clerk_id(request: Request) -> str:
    state = authenticate_request(
        request,
        AuthenticateRequestOptions(
            secret_key=settings.CLERK_SECRET_KEY,
            authorized_parties=[
                settings.FRONTEND_URL,
            ],
            accepts_token=["session_token"],
        ),
    )

    if not state.is_signed_in:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized",
        )

    clerk_id = state.payload.get("sub")

    if not clerk_id:
        raise HTTPException(
            status_code=401,
            detail="Clerk user ID not found",
        )

    return clerk_id


CurrentClerkId = Annotated[
    str,
    Depends(get_current_clerk_id),
]
