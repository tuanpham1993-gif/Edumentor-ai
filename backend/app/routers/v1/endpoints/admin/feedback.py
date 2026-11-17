
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_admin
from app.models.user import Users
from app.schemas.feedback import FeedbackResponse, FeedbackUpdate
from app.services import feedback_service


router = APIRouter(
    prefix="/admin/feedback",
    tags=["Admin - Feedback"]
)


# ==========================================
# 3. ADMIN XEM DANH SÁCH PHẢN HỒI
# ==========================================

@router.get(
    "",
    response_model=list[FeedbackResponse]
)
def get_all_feedback(
    db: Session = Depends(get_db),
    current_admin: Users = Depends(require_admin)
):
    return feedback_service.get_all_feedback(db=db)


# ==========================================
# 4. ADMIN XEM CHI TIẾT PHẢN HỒI
# ==========================================

@router.get(
    "/{feedback_id}",
    response_model=FeedbackResponse
)
def get_feedback_by_id(
    feedback_id: int,
    db: Session = Depends(get_db),
    current_admin: Users = Depends(require_admin)
):
    return feedback_service.get_feedback_by_id(
        db=db,
        feedback_id=feedback_id
    )


# ==========================================
# 5 + 6. ADMIN CẬP NHẬT TRẠNG THÁI VÀ TRẢ LỜI
# ==========================================

@router.patch(
    "/{feedback_id}",
    response_model=FeedbackResponse
)
def update_feedback(
    feedback_id: int,
    feedback_data: FeedbackUpdate,
    db: Session = Depends(get_db),
    current_admin: Users = Depends(require_admin)
):
    return feedback_service.update_feedback(
        db=db,
        feedback_id=feedback_id,
        feedback_data=feedback_data
    )


# ==========================================
# 7. ADMIN XÓA PHẢN HỒI
# ==========================================

@router.delete(
    "/{feedback_id}",
    response_model=FeedbackResponse
)
def delete_feedback(
    feedback_id: int,
    db: Session = Depends(get_db),
    current_admin: Users = Depends(require_admin)
):
    return feedback_service.delete_feedback(
        db=db,
        feedback_id=feedback_id
    )


# ==========================================
# 8. ADMIN KHÔI PHỤC PHẢN HỒI
# ==========================================

@router.patch(
    "/{feedback_id}/restore",
    response_model=FeedbackResponse
)
def restore_feedback(
    feedback_id: int,
    db: Session = Depends(get_db),
    current_admin: Users = Depends(require_admin)
):
    return feedback_service.restore_feedback(
        db=db,
        feedback_id=feedback_id
    )
