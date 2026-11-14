"""Chọn bộ chấm từ khóa theo NGÔN NGỮ của câu hỏi (module 09 · Tuấn · B3, 14/11/2026).

Ngân hàng chuyển sang tiếng Anh (D1, chốt 13/11) nhưng câu tiếng Việt cũ vẫn còn trong bài đang làm dở / lịch sử:
  - barem hoặc đề có chữ tiếng Việt có dấu → keyword_grader (bộ tiếng Việt)
  - còn lại → keyword_grader_en (bộ tiếng Anh, dựa trên khối 1 text_pipeline)
Nơi gọi (MockAI, dự phòng khi Gemini lỗi trong review_grader) chỉ cần import module này.
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
    return grader.grade_essay(rubric, answer, question)
