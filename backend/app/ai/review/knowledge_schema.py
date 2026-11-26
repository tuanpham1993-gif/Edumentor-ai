"""Khung + bộ kiểm tra đoạn tri thức do AI viết (module 09 · Tuấn · G3a, 24/11/2026).

    GEMINI_KNOWLEDGE_SCHEMA         gửi cho Gemini (responseSchema)
    check_passages(data, n, ...)    kiểm LẠI phía server → (đoạn hợp lệ, danh sách lỗi). Có lỗi → service cho viết lại 1 lần
Kiểm: đúng số đoạn · 60–250 từ (cho dư so với yêu cầu 80–200) · không trùng nhau / trùng đoạn đã có · không lẫn câu quảng
cáo (lương, giá tiền, "enroll", tên nền tảng khóa học…) · course_ids chỉ nhận id đã gửi.
"""

import re

from pydantic import BaseModel, ConfigDict, Field, ValidationError

WORDS_MIN, WORDS_MAX = 60, 250
TITLE_MAX = 200
# Dấu hiệu văn quảng cáo / số liệu thị trường. "$" chỉ bắt khi theo sau là số ("$137,000") — "$ docker ps" vẫn hợp lệ.
MARKETING = re.compile(
    r"\$\s?\d|\bsalar(y|ies)\b|\benrol(l|ment|led)?\b|\bcoursera\b|\budemy\b|\bedx\b|\bin[- ]demand\b"
    r"|\bjob market\b|\binstructor\b|\bcertificate\b|\bthis course\b",
    re.IGNORECASE,
)


class PassageOut(BaseModel):
    model_config = ConfigDict(extra="ignore")

    title: str = Field(description="Short title, max 8 words.")
    content: str = Field(description="80-200 words, one idea, plain English.")
    course_ids: list[int] = Field(default_factory=list, description="Ids of the given courses this passage covers.")


class KnowledgeOutput(BaseModel):
    passages: list[PassageOut]


GEMINI_KNOWLEDGE_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "passages": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "title": {"type": "STRING", "description": PassageOut.model_fields["title"].description},
                    "content": {"type": "STRING", "description": PassageOut.model_fields["content"].description},
                    "course_ids": {"type": "ARRAY", "items": {"type": "INTEGER"}},
                },
                "required": ["title", "content", "course_ids"],
                "propertyOrdering": ["title", "content", "course_ids"],
            },
        }
    },
    "required": ["passages"],
}


def _norm(text: str) -> str:
    return " ".join(re.sub(r"[^\w\s]", " ", (text or "").lower()).split())


def check_passages(data, n: int, *, course_ids: set[int], existing: list[str] = ()) -> tuple[list[dict], list[str]]:
    """→ (đoạn hợp lệ [{title, content, course_ids}], lỗi). Đoạn lỗi bị bỏ; lỗi dùng làm phản hồi khi viết lại."""
    try:
        output = KnowledgeOutput.model_validate(data)
    except ValidationError as err:
        return [], [f"Sai khung JSON ({err.error_count()} lỗi)"]
    seen = {_norm(e) for e in existing}
    good: list[dict] = []
    errors: list[str] = []
    for i, p in enumerate(output.passages, start=1):
        words = len(p.content.split())
        problem = None
        if not p.title.strip() or not p.content.strip():
            problem = "thiếu tiêu đề / nội dung"
        elif not WORDS_MIN <= words <= WORDS_MAX:
            problem = f"dài {words} từ (cần 80–200)"
        elif MARKETING.search(p.title + " " + p.content):
            problem = (
                f"có câu quảng cáo / số liệu thị trường ('{MARKETING.search(p.title + ' ' + p.content).group(0)}')"
            )
        elif _norm(p.content) in seen or _norm(p.title) in seen:
            problem = "trùng đoạn đã có"
        if problem:
            errors.append(f"Đoạn {i}: {problem}")
            continue
        seen.update({_norm(p.content), _norm(p.title)})
        good.append(
            {
                "title": p.title.strip()[:TITLE_MAX],
                "content": p.content.strip(),
                "course_ids": [c for c in dict.fromkeys(p.course_ids) if c in course_ids],
            }
        )
    if len(good) < n:
        errors.append(f"Cần {n} đoạn hợp lệ, mới có {len(good)}")
    return good[:n], errors
