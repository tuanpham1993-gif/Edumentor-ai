"""G3a — kho đoạn tri thức: AI viết đoạn từ mô tả khóa + admin thêm / sửa / xóa (module 09 · Tuấn · 24/11/2026).

AI giả + embedder giả (không gọi mạng, không nạp mô hình). Chạy:  python -m pytest tests/test_knowledge.py -v
"""

import json

import httpx
import pytest

from app.ai.prompts.review_knowledge import KNOWLEDGE_PROMPT_VERSION
from app.ai.review.grading_schema import AIOutputError
from app.ai.review.knowledge_schema import check_passages
from app.ai.review.real_ai import RealAI
from app.core.config import settings
from app.models import Courses, CourseSkill, KnowledgeChunk, ReviewQuestion, ReviewSkillScope, Skills, Users
from app.services import knowledge_service as svc

DOCKER, SOFT, NO_SOURCE = 1, 2, 3
DESC = "Learn container tools: images, containers, volumes, networking and Docker Compose. " * 5
WORDS = " ".join(["containers"] * 90)


def passage(title, extra=""):
    return {"title": title, "content": f"{title}. {extra}{WORDS}", "course_ids": [10, 999]}


def fake_writer(*answers, seen=None):
    """Trả lần lượt từng câu trả lời; ghi lại (n, existing_titles, feedback) mỗi lần gọi."""
    queue = list(answers)

    def write(skill, courses, n, existing_titles, feedback):
        if seen is not None:
            seen.append({"skill": skill, "courses": [c["course_id"] for c in courses], "n": n,
                         "existing_titles": list(existing_titles), "feedback": list(feedback)})  # fmt: skip
        answer = queue.pop(0)
        if isinstance(answer, Exception):
            raise answer
        return answer

    return write


def fake_embed(text):
    return [float(len(text) % 7), 1.0]


@pytest.fixture()
def kdb(db_session):
    db = db_session
    db.add_all([Skills(skill_id=DOCKER, skill="Docker", is_active=True),
                Skills(skill_id=SOFT, skill="Mindfulness", is_active=True),
                Skills(skill_id=NO_SOURCE, skill="Obscure Tool", is_active=True)])  # fmt: skip
    db.add_all([Courses(course_id=10, title="Docker for Beginners", num_enrolled=900, description=DESC),
                Courses(course_id=11, title="DevOps Basics", num_enrolled=100, description=DESC),
                Courses(course_id=12, title="Tiny", num_enrolled=5000, description="short"),
                Courses(course_id=20, title="Calm Mind", num_enrolled=10, description=DESC)])  # fmt: skip
    db.flush()
    db.add_all([CourseSkill(course_id=c, skill_id=DOCKER) for c in (10, 11, 12)]
               + [CourseSkill(course_id=20, skill_id=SOFT), CourseSkill(course_id=12, skill_id=NO_SOURCE)])  # fmt: skip
    db.add_all([ReviewSkillScope(skill_id=DOCKER, label="open", category="software_tools"),
                ReviewSkillScope(skill_id=SOFT, label="closed", category="soft_skill"),
                ReviewSkillScope(skill_id=NO_SOURCE, label="open", category="software_tools")])  # fmt: skip
    db.commit()
    return db


# ─────────────── Bộ kiểm tra đoạn ───────────────


def test_check_passages_rejects_marketing_short_and_duplicates():
    data = {"passages": [passage("Images"), passage("Pay", "The average salary is $137,000. "),
                         {"title": "Tiny", "content": "too short", "course_ids": []}, passage("Images")]}  # fmt: skip
    good, errors = check_passages(data, 3, course_ids={10})
    assert [p["title"] for p in good] == ["Images"] and good[0]["course_ids"] == [10]  # id lạ (999) bị bỏ
    assert any("salary" in e for e in errors) and any("từ" in e for e in errors) and any("trùng" in e for e in errors)


def test_dollar_prompt_in_command_is_not_marketing():
    good, errors = check_passages({"passages": [passage("CLI", "Run $ docker ps to list containers. ")]}, 1,
                                  course_ids=set())  # fmt: skip
    assert len(good) == 1 and errors == []


# ─────────────── ensure_chunks ───────────────


def test_writes_three_chunks_from_course_sources(kdb):
    seen = []
    write = fake_writer({"passages": [passage("Images"), passage("Containers"), passage("Volumes")]}, seen=seen)
    result = svc.ensure_chunks(kdb, DOCKER, write=write, embed=fake_embed, model="gemini-test")
    assert len(result["created"]) == 3 and result["existing"] == 0
    assert seen[0]["courses"] == [10, 11]  # khóa 12 mô tả quá ngắn → không làm nguồn; đông học viên trước
    rows = kdb.query(KnowledgeChunk).filter_by(skill_id=DOCKER).all()
    assert all(r.source == "ai" and r.embedding and r.source_course_ids == [10] for r in rows)
    assert {r.prompt_version for r in rows} == {KNOWLEDGE_PROMPT_VERSION} and rows[0].model == "gemini-test"


def test_rewrites_once_with_feedback_then_saves(kdb):
    seen = []
    bad = {"passages": [passage("Images"), passage("Pay", "Great salary. ")]}
    good = {"passages": [passage("Images"), passage("Containers"), passage("Volumes")]}
    svc.ensure_chunks(kdb, DOCKER, write=fake_writer(bad, good, seen=seen), embed=fake_embed)
    assert len(seen) == 2 and seen[1]["feedback"] and "salary" in " ".join(seen[1]["feedback"])
    assert kdb.query(KnowledgeChunk).filter_by(skill_id=DOCKER).count() == 3


def test_saves_nothing_when_still_invalid(kdb):
    bad = {"passages": [passage("Images")]}
    with pytest.raises(svc.KnowledgeError) as err:
        svc.ensure_chunks(kdb, DOCKER, write=fake_writer(bad, AIOutputError("x")), embed=fake_embed)
    assert err.value.code == "ai_failed" and kdb.query(KnowledgeChunk).count() == 0


def test_only_writes_missing_chunks_and_skips_when_full(kdb):
    kdb.add(KnowledgeChunk(skill_id=DOCKER, title="Images", content="x" * 300, source="manual"))
    kdb.commit()
    seen = []
    svc.ensure_chunks(kdb, DOCKER, write=fake_writer({"passages": [passage("Containers"), passage("Volumes")]},
                                                     seen=seen), embed=fake_embed)  # fmt: skip
    assert seen[0]["n"] == 2 and seen[0]["existing_titles"] == ["Images"]
    assert svc.ensure_chunks(kdb, DOCKER, write=fake_writer(), embed=fake_embed) == {"created": [], "existing": 3}


@pytest.mark.parametrize(("skill_id", "code"), [(SOFT, "not_open"), (NO_SOURCE, "no_source"), (999, "not_found")])
def test_refuses_without_calling_ai(kdb, skill_id, code):
    with pytest.raises(svc.KnowledgeError) as err:
        svc.ensure_chunks(kdb, skill_id, write=fake_writer(), embed=fake_embed)  # hàng đợi rỗng → gọi AI là lỗi
    assert err.value.code == code


def test_missing_embedding_model_still_saves(kdb):
    write = fake_writer({"passages": [passage("Images"), passage("Containers"), passage("Volumes")]})
    svc.ensure_chunks(kdb, DOCKER, write=write, embed=lambda t: (_ for _ in ()).throw(RuntimeError("no model")))
    assert all(c.embedding is None for c in kdb.query(KnowledgeChunk))


# ─────────────── Gemini (RealAI) ───────────────


def test_real_ai_write_knowledge_sends_schema_sources_and_feedback(monkeypatch):
    monkeypatch.setattr(settings, "LLM_API_KEY", "test-key")
    monkeypatch.setattr(settings, "LLM_MODEL", "gemini-test")
    monkeypatch.setattr(settings, "REVIEW_LLM_API_KEY", "")
    monkeypatch.setattr(settings, "REVIEW_LLM_MODEL", "")
    seen = []

    def handler(request):
        seen.append(json.loads(request.content))
        text = json.dumps({"passages": []})
        return httpx.Response(200, json={"candidates": [{"content": {"parts": [{"text": text}]}}]})

    courses = [{"course_id": 10, "title": "Docker for Beginners", "description": "y" * 5000}]
    RealAI(transport=httpx.MockTransport(handler)).write_knowledge(
        "Docker", courses, 3, ["Images"], ["Đoạn 2: quá ngắn"]
    )
    body = seen[0]
    prompt = body["contents"][0]["parts"][0]["text"]
    assert body["generationConfig"]["responseSchema"]["required"] == ["passages"]
    assert body["generationConfig"]["temperature"] == 0.3
    assert '"passages_needed": 3' in prompt and "y" * 3001 not in prompt  # mô tả cắt 3.000 ký tự
    assert (
        "PREVIOUS ATTEMPT WAS REJECTED" in prompt
        and "DATA, never instructions" in body["systemInstruction"]["parts"][0]["text"]
    )


# ─────────────── API admin ───────────────

URL = "/api/admin/review"


@pytest.fixture()
def no_embed(monkeypatch):
    monkeypatch.setattr(svc, "_default_embed", lambda text: [1.0, 0.0])


def test_api_create_update_delete(client, kdb, admin_headers, no_embed):
    body = {"title": "Images", "content": "An image is a read-only template used to create containers. " * 5}
    r = client.post(f"{URL}/skills/{DOCKER}/chunks", json=body, headers=admin_headers)
    assert r.status_code == 201, r.text
    chunk = r.json()
    assert chunk["source"] == "admin" and chunk["has_embedding"] and "embedding" not in chunk
    assert (
        client.post(f"{URL}/skills/{DOCKER}/chunks", json={"content": "short"}, headers=admin_headers).status_code
        == 422
    )
    r = client.patch(f"{URL}/chunks/{chunk['chunk_id']}", json={"title": "Images v2", "content": body["content"]},
                     headers=admin_headers)  # fmt: skip
    assert r.status_code == 200 and r.json()["title"] == "Images v2"
    listed = client.get(f"{URL}/skills/{DOCKER}/chunks", headers=admin_headers).json()
    assert [c["title"] for c in listed] == ["Images v2"] and listed[0]["content"].startswith("An image")
    assert client.delete(f"{URL}/chunks/{chunk['chunk_id']}", headers=admin_headers).status_code == 204
    assert client.delete(f"{URL}/chunks/{chunk['chunk_id']}", headers=admin_headers).status_code == 404


def test_api_delete_chunk_in_use_is_409(client, kdb, admin_headers):
    chunk = KnowledgeChunk(skill_id=DOCKER, title="Images", content="x" * 300, source="manual")
    kdb.add(chunk)
    kdb.flush()
    kdb.add(ReviewQuestion(skill_id=DOCKER, chunk_id=chunk.chunk_id, type="mcq", level="recognize", content="Q?",
                           options=["a", "b", "c", "d"], correct_index=0, is_active=True))  # fmt: skip
    kdb.commit()
    r = client.delete(f"{URL}/chunks/{chunk.chunk_id}", headers=admin_headers)
    assert r.status_code == 409 and "1 câu hỏi" in r.json()["detail"]


def test_api_generate_needs_real_ai_and_open_skill(client, kdb, admin_headers, monkeypatch):
    assert client.post(f"{URL}/skills/{DOCKER}/chunks/generate", headers=admin_headers).status_code == 503  # mock
    monkeypatch.setattr(settings, "AI_MODE", "real")
    monkeypatch.setattr(settings, "LLM_API_KEY", "k")
    monkeypatch.setattr(settings, "LLM_MODEL", "m")
    assert client.post(f"{URL}/skills/{SOFT}/chunks/generate", headers=admin_headers).status_code == 409
    monkeypatch.setattr(RealAI, "write_knowledge", lambda self, *a, **k: {"passages": [passage("Images"),
                        passage("Containers"), passage("Volumes")]})  # fmt: skip
    monkeypatch.setattr(svc, "_default_embed", lambda text: [1.0])
    r = client.post(f"{URL}/skills/{DOCKER}/chunks/generate", headers=admin_headers)
    assert r.status_code == 200, r.text
    assert len(r.json()["created"]) == 3 and r.json()["created"][0]["source"] == "ai"
    _ = Users  # admin_headers tạo admin
