"""Schema kết quả chấm tự luận — khối 4 (module 09 · Tuấn · B7, 15/11/2026).

Theo cách bài Session02/demo3.py (Pydantic + Field(description=...) + Literal) nhưng gọi Gemini bằng
`responseSchema` (structured output) thay cho thư viện instructor của OpenAI:
    GEMINI_RESPONSE_SCHEMA  gửi cho Gemini → mô hình buộc phải trả đúng khung (giảm lỗi JSON).
    GradingOutput           Pydantic kiểm LẠI phía server (không tin mô hình) → sai → AIOutputError → thử lại 1 lần.
Thứ tự trường mỗi ý: item → evidence → reason → result (propertyOrdering): trích căn cứ, lý giải, RỒI mới kết luận.
Không có trường điểm / độ tin cậy: điểm do CODE tính từ result (D6, D7).
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from app.ai.review.base import AIUnavailableError

Result = Literal["full", "none"]  # 15/11 (Hòa): Đạt / Không đạt, bỏ partial
REASON_MAX = 300
FEEDBACK_MAX = 600


class AIOutputError(AIUnavailableError):
    """Gemini trả về nhưng sai khung (không phải JSON, thiếu ý, nhãn lạ…) → đáng thử lại; lỗi mạng thì không.
    attempts: số lần đã gọi khi bỏ cuộc (ghi vào trace)."""

    def __init__(self, message: str, *, attempts: int = 1):
        super().__init__(message)
        self.attempts = attempts


class GradedItem(BaseModel):
    model_config = ConfigDict(extra="ignore")

    item: int = Field(description="Rubric item number, starting at 1, in rubric order.")
    evidence: str | None = Field(
        default=None, description="Exact quote copied from the student answer that supports the decision, or null."
    )
    reason: str = Field(default="", description="One short sentence explaining the decision from the meaning.")
    result: Result = Field(description="full = the item is stated correctly and clearly; none = anything else.")


class GradingOutput(BaseModel):
    model_config = ConfigDict(extra="ignore")

    items: list[GradedItem] = Field(description="One entry per rubric item, in order.")
    feedback: str | None = Field(default=None, description="2-3 short sentences of feedback to the learner.")


def _item_schema() -> dict:
    fields = GradedItem.model_fields
    return {
        "type": "OBJECT",
        "properties": {
            "item": {"type": "INTEGER", "description": fields["item"].description},
            "evidence": {"type": "STRING", "nullable": True, "description": fields["evidence"].description},
            "reason": {"type": "STRING", "description": fields["reason"].description},
            "result": {
                "type": "STRING",
                "enum": ["full", "none"],
                "description": fields["result"].description,
            },
        },
        "required": ["item", "evidence", "reason", "result"],
        "propertyOrdering": ["item", "evidence", "reason", "result"],
    }


# Khung OpenAPI rút gọn mà Gemini nhận (không có $defs / anyOf) — dựng từ Field(description) ở trên cho khỏi lệch.
GEMINI_RESPONSE_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "items": {
            "type": "ARRAY",
            "items": _item_schema(),
            "description": GradingOutput.model_fields["items"].description,
        },
        "feedback": {"type": "STRING", "description": GradingOutput.model_fields["feedback"].description},
    },
    "required": ["items", "feedback"],
    "propertyOrdering": ["items", "feedback"],
}


def parse_grading(data, n_items: int) -> GradingOutput:
    """Kiểm kết quả Gemini. Chấp nhận cả mảng trần (prompt cũ trước B7) → items, feedback = None.
    Sai bất kỳ điều gì → AIOutputError (để thử lại)."""
    if isinstance(data, list):
        data = {"items": data}
    try:
        out = GradingOutput.model_validate(data)
    except ValidationError as err:
        first = err.errors()[0]
        where = ".".join(str(p) for p in first["loc"])
        raise AIOutputError(f"Gemini trả sai khung: {where} — {first['msg']}") from None
    if len(out.items) != n_items:
        raise AIOutputError(f"Gemini chấm sai số ý (cần {n_items}, có {len(out.items)})")
    if [it.item for it in out.items] != list(range(1, n_items + 1)):
        raise AIOutputError("Gemini đánh số ý sai thứ tự")
    for it in out.items:
        it.reason = it.reason.strip()[:REASON_MAX]
    if out.feedback is not None:
        out.feedback = out.feedback.strip()[:FEEDBACK_MAX] or None
    return out
