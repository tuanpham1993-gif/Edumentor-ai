"""Khung trả về khi AI phân loại phạm vi kỹ năng (module 09 · Tuấn · G3.0, 24/11/2026).

GEMINI_SCOPE_SCHEMA  gửi cho Gemini (responseSchema) → mô hình buộc trả đúng khung
parse_scope(...)      kiểm LẠI phía server (không tin mô hình): chỉ nhận skill_id đã gửi, nhãn / nhóm hợp lệ
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from app.ai.review.grading_schema import AIOutputError
from app.models.review_skill_scope import CATEGORIES, LABELS

REASON_MAX = 200


class ScopeItem(BaseModel):
    model_config = ConfigDict(extra="ignore")

    skill_id: int = Field(description="The skill_id exactly as given.")
    label: Literal[LABELS] = Field(description="open | closed | unsure")
    category: Literal[CATEGORIES] = Field(description="One of the listed categories.")
    reason: str = Field(default="", description="Short reason, max 20 words.")


class ScopeOutput(BaseModel):
    results: list[ScopeItem]


GEMINI_SCOPE_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "results": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "skill_id": {"type": "INTEGER", "description": ScopeItem.model_fields["skill_id"].description},
                    "reason": {"type": "STRING", "description": ScopeItem.model_fields["reason"].description},
                    "label": {"type": "STRING", "enum": list(LABELS)},
                    "category": {"type": "STRING", "enum": list(CATEGORIES)},
                },
                "required": ["skill_id", "reason", "label", "category"],
                "propertyOrdering": ["skill_id", "reason", "label", "category"],  # lý do trước, nhãn sau
            },
        }
    },
    "required": ["results"],
}


def parse_scope(data, expected_ids: set[int]) -> dict[int, dict]:
    """→ {skill_id: {label, category, reason}} chỉ cho id đã gửi (id lạ bị bỏ). Sai khung → AIOutputError."""
    try:
        output = ScopeOutput.model_validate(data)
    except ValidationError as err:
        raise AIOutputError(f"Phân loại sai khung: {err.error_count()} lỗi") from None
    out: dict[int, dict] = {}
    for item in output.results:
        if item.skill_id in expected_ids and item.skill_id not in out:
            out[item.skill_id] = {"label": item.label, "category": item.category, "reason": item.reason[:REASON_MAX]}
    return out
