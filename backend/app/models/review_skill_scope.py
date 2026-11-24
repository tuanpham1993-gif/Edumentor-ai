"""Model bảng `review_skill_scopes` — phạm vi ôn tập theo kỹ năng (module 09 · Tuấn · G3.0, 24/11/2026).

Mỗi kỹ năng một nhãn, quyết định AI có được TỰ SOẠN câu ôn tập cho kỹ năng đó không (docs/guide.md Q8 sửa 22/11):
  - 'open'    Mở      — câu có đáp án đúng rõ ràng VÀ nhóm / học viên nhận ra khi AI soạn sai (Docker, SQL, Excel, Scrum…)
  - 'closed'  Không mở — kỹ năng mềm (đáp án chủ quan), chuyên ngành nhóm không kiểm chứng được (Workday, điều dưỡng…)
  - 'unsure'  Chưa rõ  — mặc định CHƯA mở; admin xem và bật nếu hợp
Kỹ năng đã có ngân hàng câu soạn tay luôn ôn được, bất kể nhãn. Chưa có dòng = coi như 'unsure'.
Bảng riêng của module 09 — KHÔNG thêm cột vào `skills` (bảng của Hòa / Khôi). Chạy lại phân loại không ghi đè nhãn admin.
"""

from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Integer, String, func

from app.core.database import Base

LABELS = ("open", "closed", "unsure")
CATEGORIES = (
    "programming",
    "software_tools",
    "data_bi",
    "infra_security",
    "software_process",
    "math_science",
    "business_domain",
    "soft_skill",
    "specialized_domain",
    "other",
)
SOURCES = ("ai", "admin")


def _in(column: str, values: tuple[str, ...]) -> str:
    return f"{column} IN ({', '.join(repr(v) for v in values)})"


class ReviewSkillScope(Base):
    __tablename__ = "review_skill_scopes"

    skill_id = Column(Integer, ForeignKey("skills.skill_id", ondelete="CASCADE"), primary_key=True)
    label = Column(String(10), nullable=False)
    category = Column(String(30), nullable=False, default="other", server_default="other")
    reason = Column(String(200), nullable=True)
    source = Column(String(10), nullable=False, default="ai", server_default="ai")
    model = Column(String(100), nullable=True)
    prompt_version = Column(String(30), nullable=True)
    updated_by = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint(_in("label", LABELS), name="ck_review_skill_scopes_label"),
        CheckConstraint(_in("category", CATEGORIES), name="ck_review_skill_scopes_category"),
        CheckConstraint(_in("source", SOURCES), name="ck_review_skill_scopes_source"),
    )
