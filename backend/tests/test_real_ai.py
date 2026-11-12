"""Test RealAI (Gemini) — KHÔNG gọi mạng: dùng httpx.MockTransport giả lập Gemini (Tuấn · 12/11/2026)."""

import json
import random

import httpx
import pytest

from app.ai.review import get_review_ai
from app.ai.review.base import AIUnavailableError, GenerationRequest, RetrievedChunk
from app.ai.review.real_ai import RealAI
from app.core.config import settings

QUESTION = {
    "content": "Phân biệt break và continue.",
    "rubric": [
        {"text": "break thoát vòng lặp", "max_points": 5, "main_keywords": ["thoát"], "sub_keywords": ["break"]},
        {"text": "continue sang lần lặp kế", "max_points": 5, "main_keywords": ["bỏ qua"], "sub_keywords": ["continue"]},
    ],
    "explanation": "Đáp án mẫu: break thoát hẳn; continue bỏ qua lần hiện tại.",
}
ANSWER = "break thì dừng luôn vòng lặp. continue thì nhảy sang vòng sau."


@pytest.fixture(autouse=True)
def gemini_settings(monkeypatch):
    monkeypatch.setattr(settings, "LLM_API_KEY", "test-key")
    monkeypatch.setattr(settings, "LLM_MODEL", "gemini-test")


def fake_gemini(payload=None, *, status=200, raw_text=None, seen=None):
    """Transport giả: trả `payload` (JSON) như Gemini; ghi request vào `seen` để kiểm."""

    def handler(request: httpx.Request) -> httpx.Response:
        if seen is not None:
            seen.append(request)
        if status != 200:
            return httpx.Response(status, json={"error": {"status": "RESOURCE_EXHAUSTED"}})
        text = raw_text if raw_text is not None else json.dumps(payload, ensure_ascii=False)
        return httpx.Response(200, json={"candidates": [{"content": {"parts": [{"text": text}]}}]})

    return httpx.MockTransport(handler)


def test_grade_by_meaning_and_points_computed_by_code():
    seen = []
    ai = RealAI(transport=fake_gemini([
        {"item": 1, "result": "full", "evidence": "break thì dừng luôn vòng lặp."},
        {"item": 2, "result": "partial", "evidence": "continue thì nhảy sang vòng sau."},
    ], seen=seen))

    results = ai.grade_essay(QUESTION, ANSWER)

    assert [r["result"] for r in results] == ["full", "partial"]
    assert [r["points"] for r in results] == [5.0, 2.5]  # điểm do code tính, không lấy từ AI
    body = json.loads(seen[0].content)
    assert seen[0].headers["x-goog-api-key"] == "test-key" and "gemini-test" in str(seen[0].url)
    assert ANSWER in body["contents"][0]["parts"][0]["text"]  # gửi bài làm…
    assert "@" not in body["contents"][0]["parts"][0]["text"]  # …không gửi email / thông tin cá nhân


def test_made_up_evidence_is_dropped():
    ai = RealAI(transport=fake_gemini([
        {"item": 1, "result": "full", "evidence": "câu này không có trong bài"},
        {"item": 2, "result": "none", "evidence": None},
    ]))
    assert [r["evidence"] for r in ai.grade_essay(QUESTION, ANSWER)] == [None, None]


def test_empty_answer_not_sent_to_ai():
    seen = []
    results = RealAI(transport=fake_gemini([], seen=seen)).grade_essay(QUESTION, "   ")
    assert [r["result"] for r in results] == ["none", "none"] and seen == []


def test_json_inside_code_fence_is_accepted():
    text = '```json\n[{"item":1,"result":"none","evidence":null},{"item":2,"result":"full","evidence":null}]\n```'
    assert [r["result"] for r in RealAI(transport=fake_gemini(raw_text=text)).grade_essay(QUESTION, ANSWER)] == ["none", "full"]


@pytest.mark.parametrize(
    "transport",
    [
        fake_gemini(status=429),  # hết lượt miễn phí
        fake_gemini(raw_text="Xin lỗi, tôi không chấm được"),  # không phải JSON
        fake_gemini([{"item": 1, "result": "full", "evidence": None}]),  # thiếu ý
        fake_gemini([{"result": "tốt"}, {"result": "full"}]),  # kết quả lạ
    ],
)
def test_bad_ai_responses_raise_unavailable(transport):
    with pytest.raises(AIUnavailableError):
        RealAI(transport=transport).grade_essay(QUESTION, ANSWER)


def test_network_timeout_raises_unavailable():
    def handler(request):
        raise httpx.ReadTimeout("chậm quá")

    with pytest.raises(AIUnavailableError):
        RealAI(transport=httpx.MockTransport(handler)).grade_essay(QUESTION, ANSWER)


def request_with(n_candidates):
    candidates = [
        {"question_id": i, "chunk_id": 1, "type": "mcq", "level": "recognize", "content": f"Câu {i}",
         "options": ["a", "b", "c", "d"], "correct_index": 0, "explanation": ""}
        for i in range(n_candidates)
    ]
    return GenerationRequest(
        course_title="Python", skill_id=1, skill_name="Python", need={"recognize": 2},
        chunks=[RetrievedChunk(chunk_id=9, code="K1", title="t", content="nội dung")],
        candidates=candidates, system_prompt="sys", prompt="user",
    )


def test_full_bank_does_not_call_ai():
    seen = []
    picked = RealAI(transport=fake_gemini([], seen=seen)).generate_questions(
        request_with(settings.REVIEW_BANK_TARGET_PER_SKILL), random.Random(0)
    )
    assert seen == [] and len(picked) == 2 and all("question_id" in q for q in picked)


def test_small_bank_asks_ai_and_fills_chunk_id():
    new = [{"type": "mcq", "level": "recognize", "content": "Mới?", "options": ["1", "2", "3", "4"], "correct_index": 1, "explanation": "x"}]
    seen = []
    out = RealAI(transport=fake_gemini(new, seen=seen)).generate_questions(request_with(3), random.Random(0))
    assert len(seen) == 1 and out[0]["chunk_id"] == 9 and "question_id" not in out[0]


def test_get_review_ai_real_mode(monkeypatch):
    monkeypatch.setattr(settings, "AI_MODE", "real")
    assert get_review_ai().name == "gemini"
    monkeypatch.setattr(settings, "LLM_API_KEY", "")
    assert get_review_ai().name == "unavailable"  # thiếu khóa → service tự dùng dự phòng
