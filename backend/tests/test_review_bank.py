"""Test GĐ7 bước 7.2 — ngân hàng câu hỏi: phiên bản, sửa nhỏ, bật / tắt, xóa, seed QT4 (module 09 · Tuấn · 13/11/2026).

Chạy:  python -m pytest tests/test_review_bank.py -v      (trong thư mục backend)
"""
# ruff: noqa: F811 — fixture import từ test_seed_review; pytest truyền qua TÊN tham số

import pytest

from app.models import (
    ReviewAnswer,
    ReviewAttempt,
    ReviewQuestion,
    ReviewQuestionMeta,
    Users,
)
from app.repositories import review_repository as repo
from app.services import review_bank_service as bank_service
from scripts import seed_review as script
from tests.test_seed_review import bank, course_312, question  # noqa: F401 — bank, course_312 là fixture


@pytest.fixture()
def seeded(db_session, course_312, bank):
    script.seed_bank(db_session, bank)
    db_session.commit()
    return bank


def by_code(db_session, code) -> ReviewQuestion:
    return db_session.query(ReviewQuestion).filter_by(code=code).one()


def use_in_attempt(db_session, q: ReviewQuestion) -> ReviewAnswer:
    """Giả lập: câu đã nằm trong một bài làm."""
    user = db_session.query(Users).first() or Users(
        full_name="Học viên", email="hv@example.com", hashed_password="x", role="student"
    )
    db_session.add(user)
    db_session.flush()
    attempt = ReviewAttempt(user_id=user.user_id, course_id=312, status="graded")
    db_session.add(attempt)
    db_session.flush()
    answer = ReviewAnswer(
        attempt_id=attempt.attempt_id,
        position=1,
        question_id=q.question_id,
        option_order=[0, 1, 2, 3] if q.type == "mcq" else None,
        max_points=0.5 if q.type == "mcq" else 1,
    )
    db_session.add(answer)
    db_session.flush()
    return answer


# ─────────────── thêm ───────────────


def test_seeded_question_has_meta_v1_approved(db_session, seeded):
    q = by_code(db_session, "312-PY-TN-01")
    meta = db_session.get(ReviewQuestionMeta, q.question_id)
    assert (meta.family_id, meta.version, meta.review_status) == (q.question_id, 1, "approved")


def test_pending_ai_question_is_inactive(db_session, seeded):
    data = {**_mcq_data(db_session), "content": "Câu AI soạn?"}
    q = bank_service.create_question(db_session, data, source="ai", review_status="pending")
    assert q.is_active is False and q.code is None
    with pytest.raises(bank_service.ActivationNotAllowedError):
        bank_service.set_active(db_session, q, True)  # QT6: phải duyệt, không bật bằng công tắc


def test_invalid_question_is_rejected(db_session, seeded):
    with pytest.raises(bank_service.QuestionInvalidError):
        bank_service.create_question(db_session, {**_mcq_data(db_session), "correct_index": 9})


def _mcq_data(db_session) -> dict:
    q = by_code(db_session, "312-PY-TN-01")
    return {
        "skill_id": q.skill_id, "chunk_id": q.chunk_id, "type": "mcq", "level": "recognize",
        "content": "Câu mới?", "options": ["a", "b", "c", "d"], "correct_index": 1, "explanation": "Vì b.",
    }


# ─────────────── sửa: tại chỗ / phiên bản ───────────────


def test_edit_unused_question_in_place(db_session, seeded):
    q = by_code(db_session, "312-PY-TN-01")
    result = bank_service.update_question(db_session, q, {"correct_index": 2})
    assert result.versioned is False and result.question is q and q.correct_index == 2


def test_edit_used_question_creates_new_version_and_keeps_history(db_session, seeded):
    q = by_code(db_session, "312-PY-TN-01")
    old_id, old_answer = q.question_id, q.correct_index
    answer = use_in_attempt(db_session, q)

    result = bank_service.update_question(db_session, q, {"correct_index": 2}, note="sửa đáp án")

    new = result.question
    assert result.versioned is True and new.question_id != old_id
    assert new.code == "312-PY-TN-01" and new.correct_index == 2 and new.is_active is True
    old = db_session.get(ReviewQuestion, old_id)
    assert old.code == "312-PY-TN-01~v1" and old.is_active is False and old.correct_index == old_answer
    assert answer.question.question_id == old_id  # bài cũ vẫn trỏ bản cũ → lịch sử đúng
    new_meta = db_session.get(ReviewQuestionMeta, new.question_id)
    assert (new_meta.family_id, new_meta.version, new_meta.change_note) == (old_id, 2, "sửa đáp án")
    # Đề chỉ còn 1 câu đang bật cho họ này
    assert [x.question_id for x in repo.bank_questions(db_session, new.skill_id) if x.code and "TN-01" in x.code] == [
        new.question_id
    ]


def test_versions_list_newest_first(db_session, seeded):
    q = by_code(db_session, "312-PY-TN-01")
    use_in_attempt(db_session, q)
    new = bank_service.update_question(db_session, q, {"correct_index": 2}).question

    history = bank_service.versions(db_session, new)

    assert [(v["version"], v["used_count"], v["is_active"]) for v in history] == [(2, 0, True), (1, 1, False)]


def test_no_change_is_noop(db_session, seeded):
    q = by_code(db_session, "312-PY-TN-01")
    result = bank_service.update_question(db_session, q, {"correct_index": q.correct_index})
    assert result.versioned is False and result.changed == []


def test_invalid_edit_changes_nothing(db_session, seeded):
    q = by_code(db_session, "312-PY-TN-01")
    with pytest.raises(bank_service.QuestionInvalidError):
        bank_service.update_question(db_session, q, {"options": ["a", "b"]})
    assert len(q.options) == 4


# ─────────────── sửa nhỏ (QT5) ───────────────


def test_minor_edit_on_used_question_stays_in_place(db_session, seeded):
    q = by_code(db_session, "312-PY-TN-01")
    use_in_attempt(db_session, q)
    result = bank_service.update_question(
        db_session, q, {"explanation": "Giải thích rõ hơn.", "exclusion_group": "PY-BLOCK"}, minor=True
    )
    assert result.versioned is False and q.explanation == "Giải thích rõ hơn."
    assert db_session.get(ReviewQuestionMeta, q.question_id).exclusion_group == "PY-BLOCK"


@pytest.mark.parametrize("changes", [{"correct_index": 2}, {"options": ["w", "x", "y", "z"]}, {"level": "understand"}])
def test_minor_edit_cannot_touch_grading_fields(db_session, seeded, changes):
    q = by_code(db_session, "312-PY-TN-01")
    with pytest.raises(bank_service.MinorEditNotAllowedError):
        bank_service.update_question(db_session, q, changes, minor=True)


def test_minor_edit_content_only_for_typos(db_session, seeded):
    q = by_code(db_session, "312-PY-TN-01")
    typo = q.content.replace("Python", "Pyhton", 1)
    original = q.content
    bank_service.update_question(db_session, q, {"content": typo}, minor=True)  # sửa chính tả: được
    assert q.content == typo
    with pytest.raises(bank_service.MinorEditNotAllowedError):
        bank_service.update_question(db_session, q, {"content": "Một đề hoàn toàn khác?"}, minor=True)
    assert original != q.content  # lần 2 không ghi gì


# ─────────────── bật / tắt / xóa ───────────────


def test_old_version_cannot_be_reactivated(db_session, seeded):
    q = by_code(db_session, "312-PY-TN-01")
    use_in_attempt(db_session, q)
    bank_service.update_question(db_session, q, {"correct_index": 2})
    with pytest.raises(bank_service.ActivationNotAllowedError):
        bank_service.set_active(db_session, q, True)


def test_toggle_active(db_session, seeded):
    q = by_code(db_session, "312-PY-TN-01")
    bank_service.set_active(db_session, q, False)
    assert q.is_active is False
    bank_service.set_active(db_session, q, True)
    assert q.is_active is True


def test_delete_unused_removes_row_and_meta(db_session, seeded):
    q = by_code(db_session, "312-PY-TN-01")
    qid = q.question_id
    assert bank_service.delete_question(db_session, q) == "deleted"
    assert db_session.get(ReviewQuestion, qid) is None and db_session.get(ReviewQuestionMeta, qid) is None


def test_delete_used_only_deactivates(db_session, seeded):
    q = by_code(db_session, "312-PY-TN-01")
    use_in_attempt(db_session, q)
    assert bank_service.delete_question(db_session, q) == "deactivated"
    assert q.is_active is False and db_session.get(ReviewQuestion, q.question_id) is not None


def test_legacy_question_without_meta_gets_meta(db_session, seeded):
    q = by_code(db_session, "312-PY-TN-01")
    db_session.delete(db_session.get(ReviewQuestionMeta, q.question_id))
    db_session.flush()
    meta = bank_service.ensure_meta(db_session, q)
    assert (meta.family_id, meta.version, meta.review_status) == (q.question_id, 1, "approved")


# ─────────────── seed QT4 ───────────────


def test_seed_twice_changes_nothing(db_session, seeded, bank):
    counts = script.seed_bank(db_session, bank)
    assert counts["questions_added"] == 0 and counts["questions_unchanged"] == len(bank["questions"])
    assert counts["questions_differ"] == [] and db_session.query(ReviewQuestion).count() == len(bank["questions"])


def test_seed_does_not_overwrite_admin_edits(db_session, seeded, bank):
    """QT4: admin đã sửa trên trang → file JSON khác DB → seed chỉ báo, không đè."""
    q = by_code(db_session, "312-PY-TN-01")
    bank_service.update_question(db_session, q, {"explanation": "Admin sửa trên trang."})

    counts = script.seed_bank(db_session, bank)

    assert counts["questions_differ"] == ["312-PY-TN-01"]
    assert q.explanation == "Admin sửa trên trang."


def test_seed_apply_changes_versions_used_question(db_session, seeded, bank):
    q = by_code(db_session, "312-PY-TN-01")
    use_in_attempt(db_session, q)
    question(bank, "312-PY-TN-01")["explanation"] = "Giải thích mới trong file."

    counts = script.seed_bank(db_session, bank, apply_changes=True)

    assert counts["questions_versioned"] == 1 and counts["questions_updated"] == 0
    new = by_code(db_session, "312-PY-TN-01")
    assert new.question_id != q.question_id and new.explanation == "Giải thích mới trong file."
    assert q.is_active is False
