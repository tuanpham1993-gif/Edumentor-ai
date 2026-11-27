"""Test B9 — Model B: chấm tự luận kèm đoạn tri thức của kỹ năng (REVIEW_GRADING_RAG) (module 09 · Tuấn · 15/11/2026).

Không gọi Gemini, không nạp mô hình embedding (embedder giả). Chạy:
    python -m pytest tests/test_review_grading_rag.py -v      (trong thư mục backend)
"""

# ruff: noqa: F811 — fixture import từ test_review_api; pytest truyền qua TÊN tham số

import pytest

from app.ai.prompts.review_grading import RAG_SUFFIX, grading_prompt
from app.ai.review import MockAI
from app.ai.review.base import RetrievedChunk
from app.core.config import settings
from app.models import KnowledgeChunk, ReviewAnswer, ReviewAttempt
from app.services import review_grader
from app.services import review_rag_service as rag
from tests.test_review_api import bank_312, start  # noqa: F401 — fixture

QUESTION = {
    "content": "Compare lists and tuples.",
    "rubric": [
        {"text": "A list can be changed", "max_points": 5},
        {"text": "A tuple cannot be changed", "max_points": 5},
    ],
    "explanation": "Model answer: lists are mutable, tuples are not.",
}


def chunk(cid, code, content="..."):
    return RetrievedChunk(chunk_id=cid, code=code, title=f"T{cid}", content=content)


def fake_embedder(vectors):
    return lambda text: vectors


# ─────────────── truy xuất ───────────────


def test_query_uses_question_and_rubric_never_the_answer():
    q = rag.grading_query(QUESTION)
    assert "Compare lists and tuples." in q and "A tuple cannot be changed" in q
    assert "mutable" not in q  # đáp án mẫu cũng không dùng — chỉ đề + barem


def test_linked_chunk_comes_first_then_by_cosine():
    chunks = [(chunk(1, "K1"), [1.0, 0.0]), (chunk(2, "K2"), [0.0, 1.0]), (chunk(3, "K3"), [0.7, 0.7])]
    ranked = rag.rank_for_grading(chunks, 2, "q", top_k=3, embedder=fake_embedder([1.0, 0.0]))
    assert [c.code for c in ranked] == ["K2", "K1", "K3"]  # K2 gắn với câu hỏi; K1 cosine 1.0 > K3 0.707
    assert ranked[0].score is None and ranked[1].score == 1.0


def test_top_k_and_no_vectors_keep_input_order():
    chunks = [(chunk(1, "K1"), None), (chunk(2, "K2"), None), (chunk(3, "K3"), None)]
    called = []
    ranked = rag.rank_for_grading(chunks, None, "q", embedder=lambda t: called.append(t))
    assert [c.code for c in ranked] == ["K1", "K2"] and called == []  # không có vector → khỏi nạp mô hình


def test_missing_embedding_model_still_returns_linked_chunk():
    chunks = [(chunk(1, "K1"), [1.0]), (chunk(2, "K2"), [1.0])]
    assert [c.code for c in rag.rank_for_grading(chunks, 2, "q", embedder=lambda t: None)] == ["K2", "K1"]


# ─────────────── prompt ───────────────


def test_prompt_adds_course_notes_and_rag_version_only_with_chunks():
    _, user, version = grading_prompt(QUESTION, "lists change")
    assert "COURSE NOTES" not in user and not version.endswith(RAG_SUFFIX)
    q = {
        **QUESTION,
        "context_chunks": [{"code": "PY-K03", "title": "Lists and tuples", "content": "A tuple is immutable."}],
    }
    _, user, version = grading_prompt(q, "lists change")
    assert "COURSE NOTES" in user and "[Note 1] Lists and tuples\nA tuple is immutable." in user
    assert "grade against the RUBRIC" in user and version == "grade-en-v4+rag"
    assert user.index("COURSE NOTES") < user.index("STUDENT ANSWER")  # bài làm vẫn là phần cuối, sau tài liệu


# ─────────────── qua review_grader + DB ───────────────


@pytest.fixture()
def rag_on(monkeypatch):
    monkeypatch.setattr(settings, "REVIEW_GRADING_RAG", True)
    monkeypatch.setattr(rag, "embed_query", lambda text: None)  # không nạp mô hình thật trong test


def essay_answers(db_session, attempt_id):
    return [
        a
        for a in db_session.query(ReviewAnswer).filter_by(attempt_id=attempt_id).order_by(ReviewAnswer.position)
        if a.question.type == "essay"
    ]


def test_flag_off_means_model_a_no_chunks(client, bank_312, student_headers, db_session):
    attempt_id = start(client, student_headers)["attempt_id"]
    a = essay_answers(db_session, attempt_id)[0]
    assert "context_chunks" not in review_grader._question_dict(a)


def test_flag_on_attaches_chunks_of_the_same_skill_linked_first(client, bank_312, student_headers, db_session, rag_on):
    attempt_id = start(client, student_headers)["attempt_id"]
    for a in essay_answers(db_session, attempt_id):
        chunks = review_grader._question_dict(a)["context_chunks"]
        assert 1 <= len(chunks) <= rag.GRADING_TOP_K
        if a.question.chunk_id is not None:
            assert chunks[0]["code"] == db_session.get(KnowledgeChunk, a.question.chunk_id).code
        skill_codes = {c.code for c in rag.review_repository.chunks_for_skill(db_session, a.question.skill_id)}
        assert {c["code"] for c in chunks} <= skill_codes


def test_retrieval_error_falls_back_to_model_a(client, bank_312, student_headers, db_session, rag_on, monkeypatch):
    attempt_id = start(client, student_headers)["attempt_id"]
    a = essay_answers(db_session, attempt_id)[0]

    def boom(*args, **kwargs):
        raise RuntimeError("db down")

    monkeypatch.setattr(rag, "retrieve_for_grading", boom)
    assert review_grader._question_dict(a)["context_chunks"] == []


def test_submit_with_rag_records_chunk_codes_in_trace(client, bank_312, student_headers, db_session, rag_on):
    attempt_id = start(client, student_headers)["attempt_id"]
    essays = essay_answers(db_session, attempt_id)
    client.patch(f"/api/review-attempts/{attempt_id}/answers", headers=student_headers,
                 json={"answers": [{"position": essays[0].position, "text_answer": "some answer text here"}]})  # fmt: skip
    response = client.post(f"/api/review-attempts/{attempt_id}/submit", headers=student_headers)
    assert response.status_code == 200, response.text

    db_session.expire_all()
    grading = db_session.get(ReviewAttempt, attempt_id).trace["grading"]
    graded = next(e for e in grading["essays"] if e["position"] == essays[0].position)
    ctx_node = next(n for n in graded["nodes"] if n["node"] == "3_context")
    assert ctx_node["output"]["rag"] is True and ctx_node["output"]["chunks"]
    assert all(set(c) == {"code", "score"} for c in ctx_node["output"]["chunks"])  # chỉ mã đoạn, không chép nội dung


def test_mock_ai_ignores_chunks_and_still_grades():
    q = {**QUESTION, "rubric": [{**r, "main_keywords": ["change"], "sub_keywords": []} for r in QUESTION["rubric"]],
         "context_chunks": [{"code": "K", "title": "t", "content": "c"}]}  # fmt: skip
    assert len(MockAI().grade_essay(q, "Lists can change. Tuples cannot change.")) == 2


# ─────────────── B12 (16/11): nạp sẵn dữ liệu NLTK lúc khởi động ───────────────


def test_warm_up_nlp_loads_nltk_and_never_raises(monkeypatch):
    from app.ai.review import text_pipeline

    calls = []
    monkeypatch.setattr(text_pipeline, "preprocess", lambda text: calls.append(text) or ["x"])
    assert rag.warm_up_nlp() is True and len(calls) == 1

    def missing(text):
        raise LookupError("Resource punkt_tab not found")

    monkeypatch.setattr(text_pipeline, "preprocess", missing)
    assert rag.warm_up_nlp() is False  # thiếu dữ liệu: chỉ ghi log, server vẫn khởi động
