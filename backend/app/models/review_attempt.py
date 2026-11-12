"""Model bảng `review_attempts` + `review_answers` — lượt làm bài ôn tập (module 09 · Tuấn · GĐ1, 10/11/2026).

ReviewAttempt — một lượt làm bài của MỘT người dùng cho MỘT khóa học:
  - status: 'in_progress' (đang làm, được Tạm rời / làm tiếp) → 'grading' (đã nộp, đang chấm
    — chấm quá thời gian, T1) → 'graded' (có điểm).
  - Mỗi người dùng + khóa có TỐI ĐA 1 lượt 'in_progress' (unique index có điều kiện bên dưới).
  - score: thang 10 (TN 12 × 0,5 + TL 1 + 1 + 2); passed = score ≥ REVIEW_PASS_SCORE.
  - is_first_pass: lượt ĐẠT ĐẦU TIÊN của khóa → lượt này làm khóa Hoàn thành + kỹ năng "Đã biết"
    (B1); các lượt đạt sau chỉ lưu lịch sử (B2).
  - trace: vết RAG — các đoạn tri thức đã truy xuất + prompt đã dựng (A4), xem qua API debug admin.

ReviewAnswer — một câu trong lượt (thứ tự 1..15):
  - option_order: thứ tự 4 lựa chọn ĐÃ XÁO khi hiển thị, vd [2, 0, 3, 1]
    (vị trí hiển thị i ↔ lựa chọn gốc option_order[i]).
  - selected_index: vị trí người dùng chọn TRÊN MÀN HÌNH (0..3); NULL = bỏ trống (= 0 điểm).
  - text_answer: bài làm tự luận.
  - max_points: điểm tối đa của câu (0,5 / 1 / 2); points: điểm đạt được sau khi chấm.
  - rubric_result: kết quả từng ý, vd [{"result": "full"|"partial"|"none", "points": 3,
    "evidence": "câu trích từ bài làm"}].
Bảng `users` là của Tuấn (models/user.py); `courses` là của Hòa/Khôi (models/course.py).
"""

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    PrimaryKeyConstraint,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.orm import relationship

from app.core.database import Base

STATUSES = ("in_progress", "grading", "graded")


class ReviewAttempt(Base):
    __tablename__ = "review_attempts"

    attempt_id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    course_id = Column(
        Integer,
        ForeignKey("courses.course_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status = Column(
        String(20), nullable=False, default="in_progress", server_default="in_progress"
    )
    score = Column(Numeric(4, 2), nullable=True)  # vd 7.70
    passed = Column(Boolean, nullable=True)  # NULL khi chưa chấm xong
    is_first_pass = Column(
        Boolean, nullable=False, default=False, server_default="false"
    )
    trace = Column(JSON(none_as_null=True), nullable=True)
    started_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    submitted_at = Column(DateTime(timezone=True), nullable=True)

    answers = relationship(
        "ReviewAnswer",
        back_populates="attempt",
        order_by="ReviewAnswer.position",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('in_progress', 'grading', 'graded')",
            name="ck_review_attempts_status",
        ),
        CheckConstraint(
            "score IS NULL OR (score >= 0 AND score <= 10)",
            name="ck_review_attempts_score",
        ),
        # Tối đa 1 lượt đang làm cho mỗi (người dùng, khóa) — DB tự chặn khi bấm "Bắt đầu" 2 lần.
        Index(
            "uq_review_attempts_one_in_progress",
            "user_id",
            "course_id",
            unique=True,
            postgresql_where=text("status = 'in_progress'"),
            sqlite_where=text("status = 'in_progress'"),
        ),
    )


class ReviewAnswer(Base):
    __tablename__ = "review_answers"

    attempt_id = Column(
        Integer,
        ForeignKey("review_attempts.attempt_id", ondelete="CASCADE"),
        nullable=False,
    )
    position = Column(Integer, nullable=False)  # thứ tự câu trên đề: 1, 2, 3…
    # RESTRICT: câu hỏi đã nằm trong bài làm thì KHÔNG xóa được (chỉ tắt is_active) — giữ lịch sử.
    question_id = Column(
        Integer,
        ForeignKey("review_questions.question_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    option_order = Column(JSON(none_as_null=True), nullable=True)  # chỉ mcq
    selected_index = Column(Integer, nullable=True)  # chỉ mcq
    text_answer = Column(Text, nullable=True)  # chỉ essay
    max_points = Column(Numeric(3, 1), nullable=False)  # 0.5 | 1.0 | 2.0
    points = Column(Numeric(4, 2), nullable=True)  # NULL khi chưa chấm
    rubric_result = Column(JSON(none_as_null=True), nullable=True)  # chỉ essay
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    attempt = relationship("ReviewAttempt", back_populates="answers")
    question = relationship("ReviewQuestion")

    __table_args__ = (
        PrimaryKeyConstraint("attempt_id", "position", name="pk_review_answers"),
        # Một câu hỏi không xuất hiện 2 lần trong cùng một đề.
        UniqueConstraint(
            "attempt_id", "question_id", name="uq_review_answers_question"
        ),
        CheckConstraint("position >= 1", name="ck_review_answers_position"),
        CheckConstraint(
            "selected_index IS NULL OR selected_index BETWEEN 0 AND 3",
            name="ck_review_answers_selected",
        ),
        CheckConstraint(
            "points IS NULL OR (points >= 0 AND points <= max_points)",
            name="ck_review_answers_points",
        ),
    )
