
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import Users
from app.schemas.feedback import FeedbackCreate, FeedbackResponse
from app.services import feedback_service


router = APIRouter(
    prefix="/feedback",
    tags=["Feedback"]
)


# ==========================================
# 1. USER GỬI PHẢN HỒI
# ==========================================

@router.post(
    "",
    response_model=FeedbackResponse,
    status_code=status.HTTP_201_CREATED
)
def create_feedback(
    feedback_data: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    return feedback_service.create_feedback(
        db=db,
        user_id=current_user.user_id,
        feedback_data=feedback_data
    )


# ==========================================
# 2. USER XEM PHẢN HỒI CỦA MÌNH
# ==========================================

@router.get(
    "/my",
    response_model=list[FeedbackResponse]
)
def get_my_feedback(
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    return feedback_service.get_my_feedback(
        db=db,
        user_id=current_user.user_id
    )
