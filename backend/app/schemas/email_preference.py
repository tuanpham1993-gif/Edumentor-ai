"""Schema API tùy chọn nhận email (module 01 · Tuấn · 11/11/2026)."""

from pydantic import BaseModel, ConfigDict


class EmailPreferencesOut(BaseModel):
    review_reminder: bool  # Nhắc ôn tập đến hạn (tối đa 1 email / tuần)
    course_suggestions: bool  # Khóa học gợi ý mới cho lộ trình
    feedback_replies: bool  # Phản hồi góp ý


class EmailPreferencesUpdate(BaseModel):
    """PATCH: gửi một phần, vd {"course_suggestions": true}. Khóa lạ → 422."""

    model_config = ConfigDict(extra="forbid")

    review_reminder: bool | None = None
    course_suggestions: bool | None = None
    feedback_replies: bool | None = None
