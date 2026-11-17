"""Model bảng `review_question_meta` — thông tin quản trị của câu hỏi ôn tập (module 09 · Tuấn · GĐ7, 13/11/2026).

Bảng PHỤ 1–1 với `review_questions` (QT8): `create_all()` không thêm được cột vào bảng đã có, nên mọi thông tin
mới của trang quản trị nằm ở đây.
  - Phiên bản (QT2, QT5): mỗi câu thuộc một HỌ (`family_id` = question_id của bản đầu tiên), `version` 1, 2, 3…
    Sửa câu ĐÃ có trong bài làm → tạo DÒNG MỚI ở review_questions (version + 1), dòng cũ tắt; bài cũ vẫn trỏ dòng cũ
    → chấm / kết quả / lịch sử không phải sửa gì.
  - Nhóm loại trừ (QT7): hai câu cùng `exclusion_group` không vào cùng một đề.
  - Trạng thái duyệt (QT6): 'pending' (AI soạn, chờ duyệt) | 'approved' | 'rejected'. Câu chưa duyệt / bị từ chối
    luôn `is_active=false` ở review_questions → không bao giờ vào đề.
Câu chưa có dòng meta (nạp trước 13/11) được coi là: họ = chính nó, phiên bản 1, đã duyệt.
"""

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)

from app.core.database import Base

REVIEW_STATUSES = ("pending", "approved", "rejected")


class ReviewQuestionMeta(Base):
    __tablename__ = "review_question_meta"

    question_id = Column(
        Integer,
        ForeignKey("review_questions.question_id", ondelete="CASCADE"),
        primary_key=True,
    )
    family_id = Column(Integer, nullable=False, index=True)  # question_id của phiên bản 1
    version = Column(Integer, nullable=False, default=1, server_default="1")
    exclusion_group = Column(String(50), nullable=True, index=True)
    review_status = Column(
        String(10), nullable=False, default="approved", server_default="approved"
    )
    reviewed_by = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    created_by = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)
    change_note = Column(Text, nullable=True)  # vd "sửa ý 2: thêm 'khi điều kiện trước sai'"
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("family_id", "version", name="uq_review_question_meta_family_version"),
        CheckConstraint("version >= 1", name="ck_review_question_meta_version"),
        CheckConstraint(
            "review_status IN ('pending', 'approved', 'rejected')",
            name="ck_review_question_meta_status",
        ),
    )
