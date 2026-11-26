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
from tests.test_question_gen import FakeAI, essay, fact, gdb, mcq  # noqa: F401 — fixture Docker Mở + 2 đoạn

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
    monkeypatch.setattr(gen, "TOPUP_ENABLED", False)  # test G3d-3 bật riêng
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


# ─────────────── G3d-3: bổ sung ~30 câu, làm lại, soạn sẵn ban đêm ───────────────


def more_mcqs(start: int, n_rec: int, n_und: int) -> dict:
    """Trắc nghiệm có đề KHÁC HẲN nhau (cổng chống trùng chữ ≥ 85%)."""
    topics = ["volumes", "networks", "registries", "tags", "healthchecks", "labels", "secrets", "compose files",
              "build args", "entrypoints", "ports", "env vars", "logs", "restarts", "prune", "layers cache",
              "multi-stage", "users", "workdirs", "copies", "ignores", "contexts", "platforms", "digests"]  # fmt: skip
    qs = []
    for i in range(n_rec + n_und):
        level = "recognize" if i < n_rec else "understand"
        q = mcq(level, 0, quote=fact(60 + start + i))  # câu nguồn riêng (cổng trùng ý — Bước A)
        q["content"] = f"Question {start + i}: what is true about Docker {topics[(start + i) % len(topics)]}?"
        qs.append(q)
    return {"questions": qs}


def test_exam_job_then_topup_to_target(gdb, sync_jobs, monkeypatch):  # noqa: F811
    monkeypatch.setattr(gen, "TOPUP_ENABLED", True)
    essays2 = {"questions": [essay("easy", 2), essay("advanced")]}  # 2 TL dễ + 1 nâng cao nữa (câu khác hẳn)
    for q in essays2["questions"]:
        q["content"] = "Compare " + q["content"].lower()
    sync_jobs["ai"] = FakeAI({
        "mcq": [{"questions": [mcq("recognize", i) for i in range(6)] + [mcq("understand", i) for i in range(6)]},
                more_mcqs(0, 7, 6)],
        "essay": [{"questions": [essay("easy", 1), essay("easy", 2), essay("advanced")]}, essays2],
    })  # fmt: skip
    exam = gen.request(gdb, SKILL, None)
    jobs = gdb.query(ReviewGenerationJob).order_by(ReviewGenerationJob.job_id).all()
    assert [j.kind for j in jobs] == ["exam", "topup"] and exam.status == "done"
    assert jobs[1].status == "done" and jobs[1].saved > 0
    assert (
        gen.usable_counts(gdb, SKILL)["recognize"] > 6
    )  # vượt khung 1 đề nhờ soạn bổ sung (đề mẫu gần giống bị cổng loại bớt)


def test_retake_without_fresh_questions_triggers_topup(client, gdb, sync_jobs, student_headers):  # noqa: F811
    sync_jobs["ai"] = full_exam_ai()
    assert client.post(f"/api/skills/{SKILL}/review-attempts", headers=student_headers).status_code == 202
    attempt = client.post(f"/api/skills/{SKILL}/review-attempts", headers=student_headers).json()
    from app.models import ReviewAttempt

    gdb.get(ReviewAttempt, attempt["attempt_id"]).status = "graded"  # nộp xong → lượt sau là làm lại
    gdb.commit()
    sync_jobs["ai"] = FakeAI({"mcq": [AIUnavailableError("503")] * 8})  # bổ sung lỗi → vẫn trả tiến độ
    r = client.post(f"/api/skills/{SKILL}/review-attempts", headers=student_headers)
    assert r.status_code == 202 and r.json()["generation"]["kind"] == "topup"
    assert r.json()["generation"]["status"] == "failed"


def test_retake_right_after_topup_ended_builds_exam(client, gdb, sync_jobs, student_headers):  # noqa: F811
    """25/11: bổ sung vừa kết thúc mà vẫn thiếu → bấm lại không tạo việc mới (không lặp soạn mãi), ráp đề lặp một phần."""
    test_retake_without_fresh_questions_triggers_topup(client, gdb, sync_jobs, student_headers)
    r = client.post(f"/api/skills/{SKILL}/review-attempts", headers=student_headers)
    assert r.status_code == 200 and len(r.json()["questions"]) == 15, r.text
    kinds = [j.kind for j in gdb.query(ReviewGenerationJob).order_by(ReviewGenerationJob.job_id)]
    assert kinds == ["exam", "topup"]  # không có việc bổ sung thứ hai


def test_poll_by_job_id_follows_exam_not_topup(client, gdb, sync_jobs, student_headers, monkeypatch):  # noqa: F811
    """25/11: việc 'exam' xong tự tạo 'topup' — màn chờ hỏi theo job_id vẫn thấy 'exam' done (không chờ thêm)."""
    monkeypatch.setattr(gen, "TOPUP_ENABLED", True)
    monkeypatch.setattr(gen, "runner", lambda job_id: None)  # việc nằm 'queued' — tự chạy từng việc bên dưới
    r = client.post(f"/api/skills/{SKILL}/review-attempts", headers=student_headers)
    exam_id = r.json()["generation"]["job_id"]
    gen.run_job(exam_id, lambda: _same_session(gdb), deps(sync_jobs["ai"]))  # xong → tạo 'topup' (đang chờ)
    url = f"/api/skills/{SKILL}/generation"
    latest = client.get(url, headers=student_headers).json()
    assert latest["kind"] == "topup" and latest["status"] == "queued"  # không job_id → việc mới nhất (như cũ)
    mine = client.get(url, headers=student_headers, params={"job_id": exam_id}).json()
    assert mine["job_id"] == exam_id and mine["status"] == "done"
    assert client.post(f"/api/skills/{SKILL}/review-attempts", headers=student_headers).status_code == 200


def test_poll_job_id_of_other_skill_404(client, gdb, sync_jobs, student_headers):  # noqa: F811
    gdb.add(Skills(skill_id=81, skill="Git", is_active=True))
    gdb.add(ReviewGenerationJob(skill_id=81, kind="exam", status="running"))
    gdb.commit()
    other = gdb.query(ReviewGenerationJob).filter_by(skill_id=81).one()
    r = client.get(f"/api/skills/{SKILL}/generation", headers=student_headers, params={"job_id": other.job_id})
    assert r.status_code == 404


def _ongoing_path(db, skill_id, learners=1):
    from app.models import LearningPath, LearningPathNode, Users

    for n in range(learners):
        user = Users(email=f"hoc{skill_id}-{n}@test.vn", full_name="Học viên", hashed_password="x")
        db.add(user)
        db.flush()
        path = LearningPath(student_id=user.user_id, original_query="q", goal_type="career", status="ongoing")
        db.add(path)
        db.flush()
        db.add(LearningPathNode(path_id=path.record_id, skill_id=skill_id, is_target=True, added_by="system",
                                is_required=True, display_order=1))  # fmt: skip
    db.commit()


def test_nightly_picks_skills_in_ongoing_paths(gdb, sync_jobs):  # noqa: F811
    from app.services import review_pregen_service as pregen

    assert pregen.pick_skills(gdb, 5) == []  # chưa ai có lộ trình
    _ongoing_path(gdb, SKILL, learners=2)
    picked = pregen.pick_skills(gdb, 5)
    assert picked[0]["skill_id"] == SKILL and picked[0]["learners"] == 2
    gdb.get(ReviewSkillScope, SKILL).label = "closed"
    gdb.commit()
    assert pregen.pick_skills(gdb, 5) == []  # không Mở → không soạn


def test_nightly_questions_wait_for_mentor(gdb, sync_jobs):  # noqa: F811
    from app.services import review_pregen_service as pregen

    _ongoing_path(gdb, SKILL)
    sync_jobs["ai"] = FakeAI({"mcq": [more_mcqs(0, 11, 12)], "essay": [{"questions": [
        essay("easy", 1), essay("easy", 2), essay("advanced")]}]})  # fmt: skip
    summary = pregen.run_nightly(lambda: _same_session(gdb), deps(sync_jobs["ai"]), limit=1)
    assert summary["done"] == 1 and summary["saved"] > 0
    metas = gdb.query(ReviewQuestionMeta).filter_by(origin="nightly").all()
    assert metas and all(m.mentor_status is None for m in metas)
    assert gen.usable_counts(gdb, SKILL) == {"recognize": 1}  # chưa mentor Đạt → chưa vào đề (D26)
    metas[0].mentor_status = "passed"
    gdb.commit()
    assert sum(gen.usable_counts(gdb, SKILL).values()) == 2
    assert not pregen.pick_skills(gdb, 5) or pregen.pick_skills(gdb, 5)[0]["missing"] != gen.missing_for(
        gdb, SKILL, "topup"
    )  # đêm sau tính cả câu soạn sẵn chờ mentor → không soạn lại hết


def test_seconds_until_next_run():
    from datetime import datetime

    from app.services.review_pregen_service import _seconds_until

    assert _seconds_until(2, datetime(2026, 11, 25, 1, 0)) == 3600
    assert _seconds_until(2, datetime(2026, 11, 25, 3, 0)) == 23 * 3600


# ─────────────── Bước B (25/11): số câu theo số ý, hết ý thì AI viết thêm đoạn ───────────────


def _small_chunks(db, mcq_facts=(1, 2, 3, 4), essay_facts=(201, 202)):
    """Đoạn ngắn: mỗi câu là một fact riêng → biết chính xác số ý. Thêm khóa nguồn để AI viết được đoạn mới."""
    from app.models import Courses, CourseSkill, KnowledgeChunk

    db.get(KnowledgeChunk, 11).content = " ".join(f"{fact(k)}." for k in essay_facts)
    db.get(KnowledgeChunk, 12).content = " ".join(f"{fact(k)}." for k in mcq_facts)
    db.add(
        Courses(course_id=70, title="Docker Basics", num_enrolled=10, description="Docker images and containers. " * 20)
    )
    db.flush()
    db.add(CourseSkill(course_id=70, skill_id=SKILL))
    db.commit()


def _ai_q(db, qid, quote, *, kind="mcq", level="recognize", active=True, reason=None, chunk=12):
    shape = ({"options": ["a", "b", "c", "d"], "correct_index": 0} if kind == "mcq" else
             {"rubric": essay()["rubric"], "explanation": "Model answer: x"})  # fmt: skip
    db.add(ReviewQuestion(question_id=qid, skill_id=SKILL, chunk_id=chunk, type=kind, level=level,
                          content=f"AI {qid}?", source="ai", is_active=active, **shape))  # fmt: skip
    db.flush()
    db.add(ReviewQuestionMeta(question_id=qid, family_id=qid, review_status="auto_approved", origin="on_demand",
                              disabled_reason=reason, ai_check={"gen": {"source_quote": quote}}))  # fmt: skip


def knowledge_writer(seen: list, start: int = 300, fail: bool = False):
    """AI viết đoạn giả: mỗi đoạn 5 câu (5 ý mới)."""
    from app.ai.review.grading_schema import AIOutputError

    counter = [start]

    def write(skill, courses, n, existing_titles, feedback):
        seen.append({"n": n, "existing_titles": list(existing_titles)})
        if fail:
            raise AIOutputError("bad json")
        out = []
        for _ in range(n):
            k = counter[0]
            counter[0] += 5
            body = " ".join(
                f"{fact(k + i)} and explains one more useful detail about containers today." for i in range(5)
            )
            out.append({"title": f"Subtopic {k}", "content": body, "course_ids": [70]})
        return {"passages": out}

    return write


def test_free_ideas_and_cap(gdb):  # noqa: F811
    from app.services import question_gen_service as qgen

    _small_chunks(gdb, mcq_facts=(1, 2, 3, 4), essay_facts=(201, 202, 203))  # 7 câu nguồn
    _ai_q(gdb, 701, fact(1))
    _ai_q(gdb, 702, fact(1), kind="essay", level="easy")  # khác loại → không trừ ý của trắc nghiệm
    _ai_q(gdb, 703, fact(2), active=False, reason="duplicate_idea")  # tắt vì trùng → vẫn tính đã dùng
    _ai_q(gdb, 704, fact(3), active=False, reason="mentor_report")  # tắt vì lỗi → trả lại ý
    gdb.commit()
    free = qgen.free_ideas(gdb, SKILL)
    assert free == {"mcq": 5, "essay": 6}
    assert qgen.cap_by_ideas({"recognize": 4, "understand": 4, "easy": 2}, free) == {
        "recognize": 4, "understand": 1, "easy": 2}  # fmt: skip
    assert qgen.ideas_short({"recognize": 4, "understand": 4, "easy": 2}, free) == 3


def test_topup_writes_more_chunks_when_out_of_ideas(gdb):  # noqa: F811
    from app.models import KnowledgeChunk

    _small_chunks(gdb)  # 4 + 2 = 6 ý / loại, bổ sung cần ~29 câu
    seen = []
    job = ReviewGenerationJob(skill_id=SKILL, kind="topup")
    gdb.add(job)
    gdb.commit()
    d = gen.Deps(write_knowledge=knowledge_writer(seen), write_questions=None, solve=None, embed=None, model="fake")
    gen._ensure_ideas(gdb, job, d)
    assert len(gdb.query(KnowledgeChunk).filter_by(skill_id=SKILL).all()) == gen.MAX_CHUNKS  # 2 → 6, không vượt
    assert seen[0]["n"] == 4 and seen[0]["existing_titles"] == ["Images", "Dockerfile"]  # chủ đề con khác
    assert len(seen) == 1  # đã tối đa → không gọi lần 2


def test_topup_stops_when_max_chunks_and_no_ideas(gdb, sync_jobs, monkeypatch):  # noqa: F811
    _small_chunks(gdb, mcq_facts=(1, 2), essay_facts=(201, 202))
    for i, k in enumerate((1, 2, 201, 202)):
        _ai_q(
            gdb, 710 + i, fact(k), level="understand", chunk=12 if k < 200 else 11
        )  # trắc nghiệm đã dùng hết 4 câu nguồn
    gdb.commit()
    monkeypatch.setattr(gen, "MAX_CHUNKS", 2)  # đã đủ đoạn → không viết thêm
    gap = gen.missing_for(gdb, SKILL, "topup")
    assert "recognize" not in gap and "understand" not in gap  # hết ý trắc nghiệm
    assert sum(gap.values()) == 4  # tự luận còn 4 câu nguồn trống
    sync_jobs["ai"] = FakeAI({"essay": [{"questions": []}] * 6})
    job = gen.request(gdb, SKILL, None, kind="topup")
    assert job.status == "done" and {c["kind"] for c in sync_jobs["ai"].calls} == {"essay"}  # không soạn trắc nghiệm


def test_extra_chunks_failure_keeps_old_chunks(gdb):  # noqa: F811
    from app.models import KnowledgeChunk

    _small_chunks(gdb)
    seen = []
    job = ReviewGenerationJob(skill_id=SKILL, kind="topup")
    gdb.add(job)
    gdb.commit()
    d = gen.Deps(write_knowledge=knowledge_writer(seen, fail=True), write_questions=None, solve=None, embed=None)
    gen._ensure_ideas(gdb, job, d)  # AI viết lỗi → không ném lỗi, soạn tiếp bằng đoạn cũ
    assert len(seen) == 2 and gdb.query(KnowledgeChunk).filter_by(skill_id=SKILL).count() == 2
