"""Model bảng `review_question_meta` — thông tin quản trị của câu hỏi ôn tập (module 09 · Tuấn · GĐ7, 13/11/2026).

Bảng PHỤ 1–1 với `review_questions` (QT8): `create_all()` không thêm được cột vào bảng đã có, nên mọi thông tin
mới của trang quản trị nằm ở đây.
  - Phiên bản (QT2, QT5): mỗi câu thuộc một HỌ (`family_id` = question_id của bản đầu tiên), `version` 1, 2, 3…
    Sửa câu ĐÃ có trong bài làm → tạo DÒNG MỚI ở review_questions (version + 1), dòng cũ tắt; bài cũ vẫn trỏ dòng cũ
    → chấm / kết quả / lịch sử không phải sửa gì.
  - Nhóm loại trừ (QT7): hai câu cùng `exclusion_group` không vào cùng một đề.
  - Trạng thái duyệt (QT6): 'pending' (AI soạn, chờ duyệt) | 'approved' | 'rejected'. Câu chưa duyệt / bị từ chối
    luôn `is_active=false` ở review_questions → không bao giờ vào đề.
    'auto_approved' (G2b · D7, 22/11): câu AI soạn cho ÔN THEO KỸ NĂNG, đã qua cổng kiểm tra tự động → dùng ngay
    (docs/guide.md Q3); admin xem lại sau. Ôn theo KHÓA vẫn chỉ dùng câu 'approved' (QT6-A).
  - ai_check (D6): kết quả cổng kiểm tra tự động, vd {"passed": true, "checks": {...}}; NULL = câu không qua cổng.
Câu chưa có dòng meta (nạp trước 13/11) được coi là: họ = chính nó, phiên bản 1, đã duyệt.
"""

from sqlalchemy import (
    JSON,
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

REVIEW_STATUSES = ("pending", "approved", "rejected", "auto_approved")


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
    review_status = Column(  # 20 ký tự: 'auto_approved' dài 13 (D7)
        String(20), nullable=False, default="approved", server_default="approved"
    )
    ai_check = Column(JSON(none_as_null=True), nullable=True)  # D6
    # G3f (25/11 — D19–D23): mentor duyệt câu AI soạn (auto_approved).
    #   disabled_reason: 'mentor_report' = câu bị tắt ngay vì mentor phản ánh lỗi (D20) → admin bác thì bật lại;
    #                    NULL = không bị tắt vì phản ánh (câu admin chủ động tắt giữ nguyên).
    #   mentor_status: NULL = chưa mentor duyệt | 'passed' = Đạt | 'reported' = bị phản ánh, chờ admin.
    disabled_reason = Column(String(20), nullable=True)
    mentor_status = Column(String(10), nullable=True)
    mentor_by = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)
    mentor_at = Column(DateTime(timezone=True), nullable=True)
    reviewed_by = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    created_by = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)
    change_note = Column(Text, nullable=True)  # vd "sửa ý 2: thêm 'khi điều kiện trước sai'"
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("family_id", "version", name="uq_review_question_meta_family_version"),
        CheckConstraint("version >= 1", name="ck_review_question_meta_version"),
        CheckConstraint(
            "review_status IN ('pending', 'approved', 'rejected', 'auto_approved')",
            name="ck_review_question_meta_status",
        ),
        CheckConstraint(
            "mentor_status IS NULL OR mentor_status IN ('passed', 'reported')",
            name="ck_review_question_meta_mentor_status",
        ),
    )
