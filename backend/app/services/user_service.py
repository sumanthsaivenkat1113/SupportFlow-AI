from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.clerk import clerk_client
from app.models.user import User


def create_or_sync_user(
    db: Session,
    clerk_id: str,
) -> User:

    # Get user from Clerk
    clerk_user = clerk_client.users.get(
        user_id=clerk_id,
    )

    # -------------------------
    # Get email
    # -------------------------

    email = None

    if clerk_user.email_addresses:
        primary_email = next(
            (
                email_address
                for email_address in clerk_user.email_addresses
                if email_address.id == clerk_user.primary_email_address_id
            ),
            None,
        )

        if primary_email:
            email = primary_email.email_address

    if not email:
        raise ValueError("Clerk user does not have a primary email address")

    # -------------------------
    # Get name
    # -------------------------

    name_parts = [
        clerk_user.first_name,
        clerk_user.last_name,
    ]

    name = " ".join(part for part in name_parts if part).strip()

    # -------------------------
    # Get image
    # -------------------------

    img_url = clerk_user.image_url

    # -------------------------
    # Find local user
    # -------------------------

    user = db.scalar(select(User).where(User.clerk_id == clerk_id))

    # -------------------------
    # Update existing user
    # -------------------------

    if user:
        user.name = name or None
        user.email = email
        user.img_url = img_url

    # -------------------------
    # Create new user
    # -------------------------

    else:
        user = User(
            clerk_id=clerk_id,
            name=name or None,
            email=email,
            img_url=img_url,
        )

        db.add(user)

    # -------------------------
    # Save
    # -------------------------

    db.commit()
    db.refresh(user)

    return user
