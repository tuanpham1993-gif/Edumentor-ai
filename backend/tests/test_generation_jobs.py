"""G3d-1 — soạn đề ở nền, lưu câu tự duyệt, ôn theo khóa không lẫn câu AI tự duyệt, nhãn phạm vi ↔ JSON (Tuấn · 25/11/2026).

AI giả (không gọi mạng), việc nền chạy ĐỒNG BỘ trong test. Docs: docs/Review-AI-Tu-Soan-On-Tap.md mục 7.5.
Chạy:  python -m pytest tests/test_generation_jobs.py -v
"""

import json
from contextlib import contextmanager

import pytest

from app.ai.review.base import AIUnavailableError
from app.models import ReviewGenerationJob, ReviewQuestion, ReviewQuestionMeta, ReviewSkillScope, Skills
from app.repositories import review_repository as repo
from app.services import review_generation_service as gen
from tests.test_question_gate import Solver
from tests.test_question_gen import FakeAI, essay, gdb, mcq  # noqa: F401 — fixture kỹ năng 80 "Docker" Mở + 2 đoạn

SKILL = 80


def full_exam_ai(extra_rounds: int = 0) -> FakeAI:
    mcqs = {"questions": [mcq("recognize", i) for i in range(6)] + [mcq("understand", i) for i in range(6)]}
    essays = {"questions": [essay("easy", 1), essay("easy", 2), essay("advanced")]}
    return FakeAI({"mcq": [mcqs] * (1 + extra_rounds), "essay": [essays] * (1 + extra_rounds)})


def deps(ai: FakeAI) -> gen.Deps:
    return gen.Deps(write_knowledge=None, write_questions=ai, solve=Solver(), embed=None, model="fake")


@contextmanager
def _same_session(db):
    yield db  # việc nền dùng CHUNG phiên của test (không đóng phiên)


@pytest.fixture()
def sync_jobs(gdb, monkeypatch):  # noqa: F811
    """Việc soạn chạy ngay (đồng bộ) với AI giả; không chờ khi AI quá tải."""
    state = {"ai": full_exam_ai()}
    monkeypatch.setattr(gen, "deps_factory", lambda: deps(state["ai"]))
    monkeypatch.setattr(
        gen, "runner", lambda job_id: gen.run_job(job_id, lambda: _same_session(gdb), deps(state["ai"]))
    )
    monkeypatch.setattr(gen, "_sleep", lambda _s: None)
    return state


# ─────────────── lỗ hổng A: ôn theo khóa không lẫn câu AI tự duyệt (D2) ───────────────


def _auto(db, qid, *, origin="on_demand", mentor=None, level="recognize"):
    db.add(ReviewQuestion(question_id=qid, skill_id=SKILL, type="mcq", level=level, content=f"Auto {qid}?",
                          options=["a", "b", "c", "d"], correct_index=0, source="ai", is_active=True))  # fmt: skip
    db.flush()
    db.add(ReviewQuestionMeta(question_id=qid, family_id=qid, review_status="auto_approved", origin=origin,
                              mentor_status=mentor))  # fmt: skip


def test_course_bank_excludes_auto_approved_skill_bank_includes(gdb):  # noqa: F811
    _auto(gdb, 501)
    _auto(gdb, 502, origin="nightly")  # soạn sẵn, mentor chưa Đạt → chưa dùng (D26)
    _auto(gdb, 503, origin="nightly", mentor="passed")
    gdb.commit()
    course = repo.bank_counts(gdb, [SKILL])
    skill = repo.bank_counts(gdb, [SKILL], include_auto=True)
    assert course[(SKILL, "recognize")] == 1  # chỉ câu soạn tay (chưa có meta = đã duyệt)
    assert skill[(SKILL, "recognize")] == 3  # + 501 (on_demand) + 503 (nightly đã Đạt), không có 502
    assert {q.question_id for q in repo.bank_questions(gdb, SKILL, include_auto=True)} >= {501, 503}
    assert 501 not in {q.question_id for q in repo.bank_questions(gdb, SKILL)}


# ─────────────── tạo việc ───────────────


def test_cannot_generate_reasons(gdb, monkeypatch):  # noqa: F811
    monkeypatch.setattr(gen, "deps_factory", lambda: None)
    assert gen.cannot_generate(gdb, SKILL) == "ai_off"
    monkeypatch.setattr(gen, "deps_factory", lambda: deps(full_exam_ai()))
    assert gen.cannot_generate(gdb, SKILL) is None
    gdb.get(ReviewSkillScope, SKILL).label = "unsure"
    gdb.commit()
    assert gen.cannot_generate(gdb, SKILL) == "not_open"


def test_one_active_job_per_skill(gdb, monkeypatch):  # noqa: F811
    started = []
    monkeypatch.setattr(gen, "deps_factory", lambda: deps(full_exam_ai()))
    monkeypatch.setattr(gen, "runner", started.append)  # không chạy → việc nằm ở 'queued'
    first = gen.request(gdb, SKILL, None)
    second = gen.request(gdb, SKILL, None)  # người thứ 2 bấm cùng lúc → chờ chung (D9)
    assert first.job_id == second.job_id and started == [first.job_id]
    assert gen.missing_for_exam(gdb, SKILL) == {"recognize": 5, "understand": 6, "easy": 2, "advanced": 1}


# ─────────────── chạy việc ───────────────


def test_job_saves_auto_approved_questions(gdb, sync_jobs):  # noqa: F811
    job = gen.request(gdb, SKILL, None)
    assert job.status == "done" and job.step == 4 and job.saved == 14  # thiếu 14 (đã có 1 câu nhận biết)
    assert job.calls == 3  # 2 lần soạn + 1 lần giải mù
    metas = gdb.query(ReviewQuestionMeta).filter_by(review_status="auto_approved").all()
    assert len(metas) == 14 and {m.origin for m in metas} == {"on_demand"}
    assert all(m.ai_check["gate"]["passed"] for m in metas)
    assert all(gdb.get(ReviewQuestion, m.question_id).is_active for m in metas)
    assert gen.missing_for_exam(gdb, SKILL) == {}


def test_overloaded_ai_waits_then_fails(gdb, sync_jobs):  # noqa: F811
    sync_jobs["ai"] = FakeAI({"mcq": [AIUnavailableError("503")] * 4})
    job = gen.request(gdb, SKILL, None)
    assert job.status == "failed" and job.error == gen.FAILED_AI and job.saved == 0


def test_short_exam_keeps_saved_questions(gdb, sync_jobs):  # noqa: F811
    bad = {"questions": [essay("easy", 1) | {"passage": 9}]}  # tự luận luôn hỏng → thiếu câu
    mcqs = {"questions": [mcq("recognize", i) for i in range(6)] + [mcq("understand", i) for i in range(6)]}
    sync_jobs["ai"] = FakeAI({"mcq": [mcqs], "essay": [bad] * 6})
    job = gen.request(gdb, SKILL, None)
    assert job.status == "failed" and job.error == gen.FAILED_SHORT and job.saved == 11  # 5 NB + 6 TH vẫn lưu
    assert len(sync_jobs["ai"].calls) == 1 + 6  # trắc nghiệm 1 lần; tự luận 2 vòng × 3 lần


def test_recover_on_startup(gdb):  # noqa: F811
    gdb.add(ReviewGenerationJob(skill_id=SKILL, kind="exam", status="running"))
    gdb.commit()
    assert gen.recover_on_startup(lambda: _same_session(gdb)) == 1
    assert gdb.query(ReviewGenerationJob).one().error == gen.FAILED_RESTART


# ─────────────── API ───────────────


def test_api_start_generates_then_opens_exam(client, gdb, sync_jobs, student_headers):  # noqa: F811
    info = client.get(f"/api/skills/{SKILL}/review", headers=student_headers).json()
    assert info["can_start"] and info["will_generate"] and info["blocked"] is None
    r = client.post(f"/api/skills/{SKILL}/review-attempts", headers=student_headers)
    assert r.status_code == 202, r.text
    assert r.json()["generation"]["status"] == "done"
    progress = client.get(f"/api/skills/{SKILL}/generation", headers=student_headers).json()
    assert progress["saved"] == 14 and progress["steps"] == 4
    r = client.post(f"/api/skills/{SKILL}/review-attempts", headers=student_headers)  # bấm lại → có đề
    assert r.status_code == 200 and len(r.json()["questions"]) == 15


def test_api_not_open_skill_says_not_open(client, gdb, sync_jobs, student_headers):  # noqa: F811
    gdb.get(ReviewSkillScope, SKILL).label = "closed"
    gdb.commit()
    info = client.get(f"/api/skills/{SKILL}/review", headers=student_headers).json()
    assert not info["can_start"] and "chưa được mở" in info["blocked"]["message"]
    r = client.post(f"/api/skills/{SKILL}/review-attempts", headers=student_headers)
    assert r.status_code == 409 and "chưa được mở" in r.json()["detail"]


def test_api_ai_off_behaves_like_g2(client, gdb, monkeypatch, student_headers):  # noqa: F811
    monkeypatch.setattr(gen, "deps_factory", lambda: None)
    r = client.post(f"/api/skills/{SKILL}/review-attempts", headers=student_headers)
    assert r.status_code == 409 and r.json()["detail"] == "Chưa có đề ôn tập cho kỹ năng này."
    assert client.get(f"/api/skills/{SKILL}/generation", headers=student_headers).status_code == 404


# ─────────────── P12: nhãn phạm vi ↔ JSON ───────────────


def test_scopes_json_roundtrip(gdb, tmp_path):  # noqa: F811
    from app.core.seed_data.skill_scopes_json import export_scopes, seed_scopes_if_empty

    gdb.add(Skills(skill_id=81, skill="Git", is_active=True))
    gdb.add(ReviewSkillScope(skill_id=81, label="closed", category="other", source="admin"))
    gdb.commit()
    path = tmp_path / "scopes.json"
    assert export_scopes(gdb, path) == 2
    assert seed_scopes_if_empty(gdb, path)["skipped"]  # bảng đã có nhãn → không nạp
    gdb.query(ReviewSkillScope).delete()
    gdb.get(Skills, 81).skill = "Git renamed"  # id 81 không còn khớp tên → bỏ dòng đó
    gdb.commit()
    rows = json.loads(path.read_text(encoding="utf-8"))
    assert {r["skill"] for r in rows} == {"Docker", "Git"}
    result = seed_scopes_if_empty(gdb, path)
    assert result == {"skipped": False, "loaded": 1, "unmatched": 1}
    assert gdb.get(ReviewSkillScope, SKILL).label == "open"
