"""Test ngân hàng câu hỏi khóa 312 + script scripts/seed_review.py (module 09 · Tuấn · GĐ1, 09/11/2026).

Chạy:  python -m pytest tests/test_seed_review.py -v      (trong thư mục backend)
"""

import copy
import sys
from collections import Counter

import pytest

from app.models import Courses, CourseSkill, KnowledgeChunk, ReviewQuestion, Skills
from scripts import seed_review as script

BANK = script.load_bank(script.DEFAULT_FILE)


@pytest.fixture()
def bank():
    return copy.deepcopy(BANK)


@pytest.fixture()
def course_312(db_session):
    """Khóa 312 + 5 kỹ năng như DB thật (đã đối chiếu 09/11)."""
    db_session.add(Courses(course_id=312, title="Python Basics: Selection and Iteration"))
    for skill_id in BANK["skills"].values():
        db_session.add(Skills(skill_id=skill_id, skill=f"skill {skill_id}", is_active=True))
    db_session.flush()
    for skill_id in BANK["skills"].values():
        db_session.add(CourseSkill(course_id=312, skill_id=skill_id))
    db_session.flush()


def question(bank, code):
    return next(q for q in bank["questions"] if q["code"] == code)


# ─────────────── File ngân hàng khóa 312 (bước 1, chốt 09/11) ───────────────


def test_bank_file_is_valid():
    assert script.validate_bank(BANK) == []


def test_bank_structure_matches_decision():
    questions = BANK["questions"]
    mcq = [q for q in questions if q["type"] == "mcq"]
    essay = [q for q in questions if q["type"] == "essay"]

    # Ngân hàng bước 2 (11/11): 20 câu / kỹ năng → 100 câu = 70 TN + 30 TL (TL dễ : nâng cao = 6 : 4)
    assert len(questions) == 100 and len(mcq) == 70 and len(essay) == 30
    assert Counter(q["level"] for q in essay) == {"easy": 18, "advanced": 12}
    # Mỗi kỹ năng: 14 TN = 7 Nhận biết + 7 Thông hiểu; 6 TL; 3 đoạn tri thức
    for code in BANK["skills"]:
        levels = Counter(q["level"] for q in mcq if q["skill"] == code)
        assert levels == {"recognize": 7, "understand": 7}, code
        assert sum(q["skill"] == code for q in essay) == 6, code
        assert sum(c["skill"] == code for c in BANK["chunks"]) == 3, code


def test_answers_are_spread_across_positions():
    """Đáp án đúng không dồn vào một vị trí (người làm không đoán mò theo vị trí được)."""
    positions = Counter(q["correct_index"] for q in BANK["questions"] if q["type"] == "mcq")
    assert len(positions) == 4
    assert max(positions.values()) <= 0.3 * sum(positions.values())  # không vị trí nào quá 30%


# ─────────────── validate_bank bắt lỗi ───────────────


@pytest.mark.parametrize(
    ("code", "change", "message"),
    [
        ("312-PY-TN-01", {"options": ["a", "b", "c"]}, "đúng 4 lựa chọn"),
        ("312-PY-TN-01", {"options": ["a", "a", "b", "c"]}, "bị trùng"),
        ("312-PY-TN-01", {"correct_index": 4}, "0..3"),
        ("312-PY-TN-01", {"level": "easy"}, "level của trắc nghiệm"),
        ("312-PY-TN-01", {"chunk": "312-ITER-K01"}, "thuộc kỹ năng khác"),
        ("312-PY-TN-01", {"chunk": "KHONG-CO"}, "không tồn tại"),
        ("312-PY-TN-01", {"skill": "XYZ"}, "không có trong skills"),
        ("312-VAR-TL-01", {"level": "advanced"}, "phải có 4–5 ý"),
        ("312-VAR-TL-01", {"options": ["a", "b", "c", "d"]}, "không được có options"),
        ("312-VAR-TL-01", {"rubric": None}, "phải có rubric"),
        ("312-VAR-TL-01", {"type": "tf"}, "type phải là"),
    ],
)
def test_validate_catches_errors(bank, code, change, message):
    question(bank, code).update(change)

    errors = script.validate_bank(bank)

    assert any(message in e for e in errors), errors


def test_validate_rubric_total_and_keywords(bank):
    rubric = question(bank, "312-PY-TL-02")["rubric"]
    rubric[0]["max_points"] = 2  # tổng còn 9
    rubric[1]["main_keywords"] = []

    errors = script.validate_bank(bank)

    assert any("tổng max_points phải = 10" in e for e in errors)
    assert any("main_keywords" in e for e in errors)


def test_validate_duplicate_codes(bank):
    bank["questions"].append(copy.deepcopy(bank["questions"][0]))
    bank["chunks"].append(copy.deepcopy(bank["chunks"][0]))

    errors = script.validate_bank(bank)

    assert sum("code bị trùng" in e for e in errors) == 2


# ─────────────── Ghi vào DB ───────────────


def test_seed_inserts_everything(db_session, course_312, bank):
    assert script.check_against_db(db_session, bank) == []

    counts = script.seed_bank(db_session, bank)

    assert counts == {
        "chunks_added": 15, "chunks_updated": 0, "questions_added": len(bank["questions"]),
        "questions_unchanged": 0, "questions_differ": [], "questions_updated": 0, "questions_versioned": 0,
    }
    q = db_session.query(ReviewQuestion).filter_by(code="312-PY-TL-02").one()
    assert q.skill_id == 167 and q.source == "bank" and len(q.rubric) == 5  # 12/11: ý cú pháp tách 3a / 3b
    assert q.chunk_id == db_session.query(KnowledgeChunk).filter_by(code="312-PY-K03").one().chunk_id


def test_seed_twice_reports_changes_without_overwriting(db_session, course_312, bank):
    """QT4 (12/11): database là nơi lưu chính — chạy lại seed KHÔNG ghi đè; câu khác file chỉ được báo."""
    script.seed_bank(db_session, bank)
    old = db_session.query(ReviewQuestion).filter_by(code="312-PY-TN-01").one().explanation
    question(bank, "312-PY-TN-01")["explanation"] = "Giải thích mới"

    counts = script.seed_bank(db_session, bank)

    assert counts["questions_added"] == 0 and counts["questions_differ"] == ["312-PY-TN-01"]
    assert counts["questions_unchanged"] == len(bank["questions"]) - 1
    assert db_session.query(ReviewQuestion).count() == len(bank["questions"])
    assert db_session.query(KnowledgeChunk).count() == 15
    assert db_session.query(ReviewQuestion).filter_by(code="312-PY-TN-01").one().explanation == old

    counts = script.seed_bank(db_session, bank, apply_changes=True)  # chưa ai làm → sửa tại chỗ
    assert counts["questions_updated"] == 1 and counts["questions_versioned"] == 0
    assert db_session.query(ReviewQuestion).filter_by(code="312-PY-TN-01").one().explanation == "Giải thích mới"


def test_changed_chunk_content_resets_embedding(db_session, course_312, bank):
    script.seed_bank(db_session, bank)
    chunk = db_session.query(KnowledgeChunk).filter_by(code="312-PY-K01").one()
    chunk.embedding = [0.1, 0.2]
    db_session.flush()

    bank["chunks"][0]["content"] = "Nội dung đã sửa"
    script.seed_bank(db_session, bank)

    assert chunk.embedding is None


def test_seed_keeps_disabled_question_disabled(db_session, course_312, bank):
    script.seed_bank(db_session, bank)
    q = db_session.query(ReviewQuestion).filter_by(code="312-PY-TN-01").one()
    q.is_active = False

    script.seed_bank(db_session, bank)

    assert q.is_active is False


def test_skill_not_in_course_is_rejected(db_session, course_312, bank):
    bank["skills"]["PY"] = 999

    errors = script.check_against_db(db_session, bank)

    assert errors == ["Kỹ năng PY (skill_id 999) không thuộc khóa 312"]


# ─────────────── Lệnh main() ───────────────


def run_main(monkeypatch, db_session, path=script.DEFAULT_FILE):
    monkeypatch.setattr(sys, "argv", ["seed_review", "--file", str(path)])
    monkeypatch.setattr(script, "SessionLocal", lambda: db_session)
    monkeypatch.setattr(script, "create_tables", lambda: None)
    monkeypatch.setattr(db_session, "close", lambda: None)  # giữ phiên test để kiểm tra sau
    return script.main()


def test_main_success(db_session, course_312, monkeypatch, capsys):
    code = run_main(monkeypatch, db_session)

    assert code == 0
    assert f"câu hỏi +{len(BANK['questions'])}" in capsys.readouterr().out
    assert db_session.query(ReviewQuestion).count() == len(BANK["questions"])


def test_main_invalid_file_writes_nothing(db_session, course_312, monkeypatch, capsys, tmp_path, bank):
    question(bank, "312-PY-TN-01")["correct_index"] = 9
    bad = tmp_path / "bad.json"
    bad.write_text(script.json.dumps(bank, ensure_ascii=False), encoding="utf-8")

    code = run_main(monkeypatch, db_session, bad)

    assert code == 1
    assert "KHÔNG nạp" in capsys.readouterr().out
    assert db_session.query(ReviewQuestion).count() == 0
