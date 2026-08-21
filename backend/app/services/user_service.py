"""
Single-user stand-in for auth.

This app doesn't have authentication yet (not in the MVP feature list),
so resume uploads and applications need *some* user to belong to. This
creates/reuses one fixed local user rather than requiring a login flow.
When real auth is added later, this becomes unnecessary — nothing else
needs to change, since every table already has a proper user_id FK.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User

DEFAULT_USER_EMAIL = "you@local.dev"


def get_or_create_default_user(db: Session) -> User:
    stmt = select(User).where(User.email == DEFAULT_USER_EMAIL)
    user = db.execute(stmt).scalar_one_or_none()
    if user is None:
        user = User(email=DEFAULT_USER_EMAIL, hashed_password="unused-no-auth-yet")
        db.add(user)
        db.flush()
    return user
