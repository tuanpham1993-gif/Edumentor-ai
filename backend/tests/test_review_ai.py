"""Test validator, mock AI, RAG, prompt của module 09 (Tuấn · GĐ2, 09/11/2026).

Chạy:  python -m pytest tests/test_review_ai.py -v      (trong thư mục backend)
"""

import random

import pytest

from app.ai.prompts.review import build_generation_prompt
from app.ai.review import MockAI, get_review_ai
from app.ai.review.base import AIUnavailableError, GenerationRequest, RetrievedChunk
from app.ai.review.mock_ai import pick_from_bank
from app.ai.review.validator import generated_errors, question_errors
from app.core.config import settings
from app.models import KnowledgeChunk, Skills
from app.services import rag_service


def mcq(qid, level="recognize", chunk_id=None):
    return {
        "question_id": qid,
        "chunk_id": chunk_id,
        "type": "mcq",
        "level": level,
        "content": f"Câu {qid}?",
        "options": ["a", "b", "c", "d"],
        "correct_index": 0,
    }


# ─────────────── validator ───────────────


def test_question_errors_valid_and_invalid():
    assert question_errors(mcq(1)) == []
    assert question_errors("không phải dict") == ["Câu: phải là object"]
    assert any("correct_index" in e for e in question_errors({**mcq(1), "correct_index": True}))


def test_generated_errors_checks_counts_and_duplicates():
    need = {"recognize": 2, "understand": 1}
    good = [mcq(1), mcq(2), mcq(3, "understand")]

    assert generated_errors(good, need) == []
    assert any("Sai số câu" in e for e in generated_errors(good[:2], need))
    assert any("trùng" in e for e in generated_errors([mcq(1), mcq(1), mcq(3, "understand")], need))
    assert generated_errors("không phải list", need) == ["Kết quả AI phải là danh sách câu hỏi"]


# ─────────────── mock AI ───────────────


def test_pick_prefers_rag_chunks_and_avoids_previous():
    candidates = [mcq(1, chunk_id=10), mcq(2, chunk_id=20), mcq(3, chunk_id=10), mcq(4, chunk_id=20)]

    for seed in range(20):
        picked = pick_from_bank(
            candidates, {"recognize": 2}, random.Random(seed), prefer_chunk_ids={10}, avoid_question_ids={3}
        )
        ids = {q["question_id"] for q in picked}
        assert 1 in ids  # thuộc đoạn RAG + chưa dùng → luôn được chọn
        assert 3 not in ids  # lượt trước đã dùng → tránh khi còn câu khác


def test_pick_repeats_previous_only_when_nothing_else():
    picked = pick_from_bank([mcq(1), mcq(2)], {"recognize": 2}, random.Random(0), avoid_question_ids={1, 2})
    assert {q["question_id"] for q in picked} == {1, 2}


def test_mock_ai_uses_retrieved_chunks():
    request = GenerationRequest(
        course_title="Khóa",
        skill_id=1,
        skill_name="Iteration",
        need={"recognize": 1},
        chunks=[RetrievedChunk(chunk_id=20, code="K2", title=None, content="...")],
        candidates=[mcq(1, chunk_id=10), mcq(2, chunk_id=20)],
    )
    for seed in range(10):
        assert MockAI().generate_questions(request, random.Random(seed))[0]["question_id"] == 2


def test_get_review_ai_by_mode(monkeypatch):
    assert get_review_ai().name == "mock"

    # AI_MODE=real nhưng thiếu khóa → AI "không dùng được" (service tự dùng dự phòng).
    # Đặt khóa rỗng để test KHÔNG phụ thuộc .env trên máy (máy có khóa thật sẽ ra RealAI — xem test_real_ai.py).
    monkeypatch.setattr(settings, "AI_MODE", "real")
    monkeypatch.setattr(settings, "LLM_API_KEY", "")
    with pytest.raises(AIUnavailableError):
        get_review_ai().generate_questions(None, random.Random(0))


# ─────────────── prompt ───────────────


def test_generation_prompt_contains_context_and_counts():
    chunks = [RetrievedChunk(chunk_id=1, code="K1", title="Vòng lặp for", content="for duyệt dãy")]

    prompt = build_generation_prompt(
        course_title="Python Basics", skill_name="Iteration", chunks=chunks, need={"recognize": 2, "easy": 0}
    )

    assert "Kỹ năng cần ôn: Iteration" in prompt
    assert "[Đoạn 1] Vòng lặp for" in prompt and "for duyệt dãy" in prompt
    assert "2 câu trắc nghiệm mức Nhận biết" in prompt
    assert "tự luận DỄ" not in prompt  # mức độ cần 0 câu thì không yêu cầu


# ─────────────── RAG ───────────────


def test_cosine():
    assert rag_service.cosine([1, 0], [1, 0]) == pytest.approx(1)
    assert rag_service.cosine([1, 0], [0, 1]) == pytest.approx(0)
    with pytest.raises(ValueError):
        rag_service.cosine([1, 0], [1, 0, 0])


@pytest.fixture()
def chunks(db_session):
    db_session.add(Skills(skill_id=400, skill="Iteration", is_active=True))
    db_session.flush()
    rows = [
        KnowledgeChunk(code="K1", skill_id=400, content="while", embedding=[0.0, 1.0]),
        KnowledgeChunk(code="K2", skill_id=400, content="for", embedding=[1.0, 0.0]),
        KnowledgeChunk(code="K3", skill_id=400, content="break", embedding=[0.7, 0.7]),
    ]
    db_session.add_all(rows)
    db_session.flush()
    return rows


def test_retrieve_ranks_by_cosine(db_session, chunks):
    result = rag_service.retrieve_chunks(db_session, 400, "vòng lặp for", top_k=2, embedder=lambda _: [1.0, 0.0])

    assert [c.code for c in result] == ["K2", "K3"]
    assert result[0].score == pytest.approx(1.0)


def test_retrieve_without_embeddings_skips_model(db_session, chunks):
    for c in chunks:
        c.embedding = None
    db_session.flush()

    def must_not_be_called(_):
        raise AssertionError("không được nạp mô hình khi đoạn chưa có vector")

    result = rag_service.retrieve_chunks(db_session, 400, "x", embedder=must_not_be_called)

    assert [c.code for c in result] == ["K1", "K2", "K3"]  # theo thứ tự tạo
    assert all(c.score is None for c in result)


def test_retrieve_when_model_unavailable_or_wrong_dimension(db_session, chunks):
    no_model = rag_service.retrieve_chunks(db_session, 400, "x", embedder=lambda _: None)
    wrong_dim = rag_service.retrieve_chunks(db_session, 400, "x", embedder=lambda _: [1.0, 0.0, 0.0])

    for result in (no_model, wrong_dim):
        assert [c.code for c in result] == ["K1", "K2", "K3"]
        assert all(c.score is None for c in result)
