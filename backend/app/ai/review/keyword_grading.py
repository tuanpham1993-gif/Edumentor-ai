"""Chọn bộ chấm từ khóa theo NGÔN NGỮ của câu hỏi (module 09 · Tuấn · B3, 14/11/2026).

Ngân hàng chuyển sang tiếng Anh (D1, chốt 13/11) nhưng câu tiếng Việt cũ vẫn còn trong bài đang làm dở / lịch sử:
  - barem hoặc đề có chữ tiếng Việt có dấu → keyword_grader (bộ tiếng Việt)
  - còn lại → keyword_grader_en (bộ tiếng Anh, dựa trên khối 1 text_pipeline)
Nơi gọi (MockAI, dự phòng khi Gemini lỗi trong review_grader) chỉ cần import module này.

15/11 (Hòa): mỗi ý chỉ Đạt / Không đạt. Hai bộ chấm bên trong vẫn phân biệt "partial" (có từ khóa nhưng thiếu
chủ thể, bài quá ngắn, liệt kê từ khóa…) — ở đây quy về "none" = 0 điểm: chưa nêu rõ ý thì không đạt.
"""

import re

from app.ai.review import keyword_grader, keyword_grader_en

_VIETNAMESE = re.compile("[àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]", re.IGNORECASE)


def is_vietnamese(rubric: list[dict], question: str | None = None) -> bool:
    parts = [question or ""]
    for item in rubric:
        parts.append(item.get("text") or "")
        parts += item.get("main_keywords") or []
        parts += item.get("sub_keywords") or []
    return bool(_VIETNAMESE.search(" ".join(parts)))


def grade_essay(rubric: list[dict], answer: str | None, question: str | None = None) -> list[dict]:
    grader = keyword_grader if is_vietnamese(rubric, question) else keyword_grader_en
    return [_binary(r) for r in grader.grade_essay(rubric, answer, question)]


def _binary(result: dict) -> dict:
    if result["result"] == "full":
        return result
    return {**result, "result": "none", "points": 0.0, "evidence": None}
