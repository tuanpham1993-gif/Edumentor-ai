
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.feedback import Feedback
from app.schemas.feedback import FeedbackCreate, FeedbackUpdate


# ==========================================
# 1. USER GỬI PHẢN HỒI
# ==========================================

def create_feedback(
    db: Session,
    user_id: int,
    feedback_data: FeedbackCreate
):
    new_feedback = Feedback(
        user_id=user_id,
        **feedback_data.model_dump()
    )

    db.add(new_feedback)
    db.commit()
    db.refresh(new_feedback)

    return new_feedback


# ==========================================
# 2. USER XEM PHẢN HỒI CỦA MÌNH
# ==========================================

def get_my_feedback(
    db: Session,
    user_id: int
):
    feedbacks = (
        db.query(Feedback)
        .filter(
            Feedback.user_id == user_id,
            Feedback.is_deleted == False
        )
        .order_by(Feedback.created_at.desc())
        .all()
    )

    return feedbacks


# ==========================================
# 3. ADMIN XEM DANH SÁCH PHẢN HỒI
# ==========================================

def get_all_feedback(db: Session):
    feedbacks = (
        db.query(Feedback)
        .filter(Feedback.is_deleted == False)
        .order_by(Feedback.created_at.desc())
        .all()
    )

    return feedbacks


# ==========================================
# 4. ADMIN XEM CHI TIẾT PHẢN HỒI
# ==========================================

def get_feedback_by_id(
    db: Session,
    feedback_id: int
):
    feedback = (
        db.query(Feedback)
        .filter(
            Feedback.feedback_id == feedback_id,
            Feedback.is_deleted == False
        )
        .first()
    )

    if not feedback:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy phản hồi"
        )

    return feedback


# ==========================================
# 5 + 6. ADMIN CẬP NHẬT TRẠNG THÁI VÀ TRẢ LỜI
# ==========================================

def update_feedback(
    db: Session,
    feedback_id: int,
    feedback_data: FeedbackUpdate
):
    feedback = get_feedback_by_id(db, feedback_id)

    feedback.status = feedback_data.status

    if feedback_data.admin_response is not None:
        feedback.admin_response = feedback_data.admin_response
        feedback.responded_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(feedback)

    return feedback


# ==========================================
# 7. ADMIN XÓA PHẢN HỒI
# ==========================================

def delete_feedback(
    db: Session,
    feedback_id: int
):
    feedback = get_feedback_by_id(db, feedback_id)

    feedback.is_deleted = True
    feedback.deleted_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(feedback)

    return feedback


# ==========================================
# 8. ADMIN KHÔI PHỤC PHẢN HỒI
# ==========================================

def restore_feedback(
    db: Session,
    feedback_id: int
):
    feedback = (
        db.query(Feedback)
        .filter(
            Feedback.feedback_id == feedback_id,
            Feedback.is_deleted == True
        )
        .first()
    )

    if not feedback:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy phản hồi đã xóa"
        )

    feedback.is_deleted = False
    feedback.deleted_at = None

    db.commit()
    db.refresh(feedback)

    return feedback
