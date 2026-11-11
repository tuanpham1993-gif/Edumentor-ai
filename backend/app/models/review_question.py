"""Model bảng `review_questions` — ngân hàng câu hỏi ôn tập (module 09 · Tuấn · GĐ1, 10/11/2026).

Mỗi dòng = một câu hỏi về MỘT kỹ năng. Hai loại (chốt 09/11):
  - type='mcq'   (trắc nghiệm, 0,5đ): level 'recognize' (Nhận biết) | 'understand' (Thông hiểu)
                 options = 4 lựa chọn (JSON), correct_index = 0..3 (vị trí đáp án đúng TRƯỚC khi xáo)
  - type='essay' (tự luận):          level 'easy' (dễ, barem 2–3 ý, 1đ) | 'advanced' (nâng cao, 4–5 ý, 2đ)
                 rubric = danh sách ý, mỗi ý:
                 {"text": "...", "max_points": 3, "main_keywords": [...], "sub_keywords": [...]}
                 (tổng max_points = 10; chấm mock theo từ khóa — A10)
  - source: 'bank' (soạn tay, đã duyệt) | 'ai' (AI sinh, qua validator — giai đoạn 2)
  - is_active=false: tắt câu sai thay vì xóa → lịch sử bài cũ vẫn xem được (Q10).
  - code: mã duy nhất do người soạn đặt (vd "312-ITER-TN-01") → seed chạy lại không trùng.
Số ý / tổng điểm barem do validator kiểm tra (JSON khó ràng buộc ở tầng DB).
"""

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)

from app.core.database import Base

TYPES = ("mcq", "essay")
MCQ_LEVELS = ("recognize", "understand")
ESSAY_LEVELS = ("easy", "advanced")
SOURCES = ("bank", "ai")


class ReviewQuestion(Base):
    __tablename__ = "review_questions"

    question_id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True, nullable=True)
    skill_id = Column(
        Integer,
        ForeignKey("skills.skill_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # Câu hỏi sinh từ đoạn tri thức nào (RAG). Xóa đoạn → câu hỏi vẫn giữ, chỉ mất liên kết.
    chunk_id = Column(
        Integer,
        ForeignKey("knowledge_chunks.chunk_id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    type = Column(String(10), nullable=False)
    level = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    # none_as_null=True: Python None → SQL NULL (mặc định SQLAlchemy lưu chuỗi JSON 'null',
    # khiến CHECK "options IS NOT NULL" bị lọt — test_review_models bắt được lỗi này).
    options = Column(JSON(none_as_null=True), nullable=True)  # chỉ mcq
    correct_index = Column(Integer, nullable=True)  # chỉ mcq
    rubric = Column(JSON(none_as_null=True), nullable=True)  # chỉ essay
    explanation = Column(Text, nullable=True)
    source = Column(String(10), nullable=False, default="bank", server_default="bank")
    is_active = Column(Boolean, nullable=False, default=True, server_default="true")
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        CheckConstraint("type IN ('mcq', 'essay')", name="ck_review_questions_type"),
        # Mức độ phải khớp loại câu: TN chỉ NB/TH, TL chỉ dễ/nâng cao.
        CheckConstraint(
            "(type = 'mcq' AND level IN ('recognize', 'understand'))"
            " OR (type = 'essay' AND level IN ('easy', 'advanced'))",
            name="ck_review_questions_level",
        ),
        # TN: có lựa chọn + đáp án 0..3, không có barem. TL: có barem, không có lựa chọn / đáp án.
        CheckConstraint(
            "(type = 'mcq' AND options IS NOT NULL AND correct_index BETWEEN 0 AND 3"
            " AND rubric IS NULL)"
            " OR (type = 'essay' AND rubric IS NOT NULL AND options IS NULL"
            " AND correct_index IS NULL)",
            name="ck_review_questions_shape",
        ),
        CheckConstraint("source IN ('bank', 'ai')", name="ck_review_questions_source"),
    )
