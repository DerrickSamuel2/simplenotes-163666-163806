from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_session
from app.models.user import User
from app.schemas.user import UserPublic, UserUpdate
from app.core.integrations import BackupService, AnalyticsService

router = APIRouter()

@router.get("/me", response_model=UserPublic, summary="Get current user", description="Retrieve the current authenticated user's profile.")
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.patch("/me", response_model=UserPublic, summary="Update profile", description="Update profile attributes and privacy settings.")
def update_me(payload: UserUpdate, db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    if payload.full_name is not None:
        current_user.full_name = payload.full_name
    if payload.allow_analytics is not None:
        current_user.allow_analytics = payload.allow_analytics
    if payload.private_account is not None:
        current_user.private_account = payload.private_account
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    AnalyticsService().track(current_user.id, "profile_updated", None)
    return current_user

@router.get("/me/export", summary="Export my data", description="Export user data via backup provider (stub).")
def export_me(current_user: User = Depends(get_current_user)):
    url = BackupService().export_user_data(current_user.id)
    return {"status": "ok", "location": url}
