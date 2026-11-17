
from typing import Literal, Optional
from datetime import datetime

from pydantic import BaseModel, ConfigDict


TargetType = Literal["course", "skill", "system", "other"]

FeedbackStatus = Literal["pending", "in_review", "resolved", "rejected"]


class FeedbackBase(BaseModel):
    target_type: TargetType
    course_id: Optional[int] = None
    skill_id: Optional[int] = None
    feedback_type: Optional[str] = None
    title: Optional[str] = None
    content: str
    image_url: Optional[str] = None


class FeedbackCreate(FeedbackBase):
    pass


class FeedbackResponse(FeedbackBase):
    model_config = ConfigDict(from_attributes=True)

    feedback_id: int
    user_id: int
    status: FeedbackStatus
    admin_response: Optional[str] = None
    responded_at: Optional[datetime] = None
    created_at: datetime


class FeedbackUpdate(BaseModel):
    status: FeedbackStatus
    admin_response: Optional[str] = None
