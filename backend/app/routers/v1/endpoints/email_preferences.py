"""API tùy chọn nhận email (module 01 · Tuấn · 11/11/2026). Prefix /api/me/email-preferences.

    GET   /api/me/email-preferences  — 3 công tắc (chưa lưu → mặc định)
    PATCH /api/me/email-preferences  — đổi một phần, vd {"course_suggestions": true}
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import Users
from app.schemas.email_preference import EmailPreferencesOut, EmailPreferencesUpdate
from app.services import email_preference_service

router = APIRouter()


@router.get("", response_model=EmailPreferencesOut, summary="Tùy chọn nhận email của tôi")
def read_email_preferences(
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return email_preference_service.get_preferences(db, current_user.user_id)


@router.patch("", response_model=EmailPreferencesOut, summary="Bật / tắt từng loại email")
def update_email_preferences(
    request: EmailPreferencesUpdate,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    changes = request.model_dump(exclude_none=True)
    return email_preference_service.update_preferences(db, current_user.user_id, changes)
