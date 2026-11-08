"""Schema kỹ năng trong hồ sơ /api/me/skills (module 01 · Tuấn · GĐ4, 08/11/2026).

- SkillStatus  : chỉ 'known' (đã biết) hoặc 'learning' (đang học) — khớp CHECK của bảng user_skills.
- UserSkillOut : một kỹ năng trả về cho frontend (kèm TÊN kỹ năng lấy từ bảng skills của Hòa).
- SkillChange / UpdateSkillsRequest : body PATCH /api/me/skills (4.3) — 3 nhóm add / update / remove (S1).
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator

# Literal: FastAPI / Pydantic tự từ chối (422) mọi giá trị khác 'known' | 'learning'.
SkillStatus = Literal["known", "learning"]
SkillSource = Literal["manual", "course", "review"]


class UserSkillOut(BaseModel):
    skill_id: int
    skill: str  # tên kỹ năng, vd "Python Programming"
    status: SkillStatus
    source: SkillSource  # S5: kỹ năng vào hồ sơ từ đâu
    updated_at: datetime


MAX_CHANGES = 200  # một lần lưu tối đa 200 thay đổi — chặn request khổng lồ


class SkillChange(BaseModel):
    """Một kỹ năng cần thêm hoặc đổi trạng thái."""

    skill_id: int = Field(gt=0)
    status: SkillStatus


class UpdateSkillsRequest(BaseModel):
    """PATCH /api/me/skills — mọi thay đổi của MỘT lần bấm "Lưu" (FR-04, S1).

    {"add": [{"skill_id": 12, "status": "learning"}],
     "update": [{"skill_id": 5, "status": "known"}],
     "remove": [7]}
    Nhóm nào không có thay đổi thì bỏ trống (mặc định []).
    """

    add: list[SkillChange] = []
    update: list[SkillChange] = []
    remove: list[int] = []

    @model_validator(mode="after")
    def check_changes(self) -> "UpdateSkillsRequest":
        ids = (
            [c.skill_id for c in self.add]
            + [c.skill_id for c in self.update]
            + list(self.remove)
        )
        if not ids:
            raise ValueError("Không có thay đổi nào để lưu.")
        if len(ids) > MAX_CHANGES:
            raise ValueError(f"Mỗi lần lưu tối đa {MAX_CHANGES} thay đổi.")
        if any(i <= 0 for i in self.remove):
            raise ValueError("skill_id không hợp lệ.")
        # Một kỹ năng chỉ được xuất hiện MỘT lần trong cả 3 nhóm (vd vừa add vừa remove → mơ hồ).
        repeated = sorted({i for i in ids if ids.count(i) > 1})
        if repeated:
            raise ValueError(
                f"Kỹ năng xuất hiện nhiều lần trong cùng một lần lưu: {repeated}."
            )
        return self
