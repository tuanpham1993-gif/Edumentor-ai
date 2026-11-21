"""Tự nạp đề ôn tập khi database mới (app/core/seed_data/review_autoseed.py · Tuấn · 21/11/2026).

Chạy:  python -m pytest tests/test_review_autoseed.py -v      (trong thư mục backend)
"""

# ruff: noqa: F811 — fixture course_312 import từ test_seed_review; pytest truyền qua TÊN tham số

import json

from app.core.seed_data import review_autoseed as auto
from app.core.seed_data import seed_review
from app.models import KnowledgeChunk, ReviewQuestion
from tests.test_seed_review import course_312  # noqa: F401 — fixture: khóa 312 + 5 kỹ năng


class FakeModel:
    def encode(self, texts, normalize_embeddings=True):
        import numpy as np

        return np.array([[0.6, 0.8]] * len(texts))


def session_factory(db_session):
    class _Session:
        def __call__(self):
            return self

        def __getattr__(self, name):
            return getattr(db_session, name)

        def close(self):  # giữ phiên test
            pass

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

    return _Session()


def test_bank_files_are_current_english_banks_only():
    names = [p.name for p in auto.bank_files()]
    assert names == sorted(names) and "course_312_en.json" in names
    assert all(n.endswith("_en.json") for n in names)  # không lấy archive/course_312.json


def test_empty_database_loads_every_bank_whose_course_exists(db_session, course_312):
    result = auto.seed_banks_if_empty(db_session)

    assert result["skipped"] is False and result["loaded"] == ["course_312_en.json"]
    assert set(result["failed"]) == {p.name for p in auto.bank_files()} - {"course_312_en.json"}  # khóa chưa có
    assert db_session.query(ReviewQuestion).count() == len(seed_review.load_bank(seed_review.DEFAULT_FILE)["questions"])


def test_existing_bank_is_never_reloaded(db_session, course_312):
    auto.seed_banks_if_empty(db_session)
    first = db_session.query(ReviewQuestion).first()
    db_session.delete(first)  # admin xóa một câu
    db_session.commit()
    count = db_session.query(ReviewQuestion).count()

    assert auto.seed_banks_if_empty(db_session) == {"skipped": True, "loaded": [], "failed": []}
    assert db_session.query(ReviewQuestion).count() == count  # câu đã xóa không quay lại


def test_broken_file_is_skipped_without_crashing(db_session, course_312, tmp_path):
    db_session.commit()  # như DB thật: khóa học đã lưu trước khi nạp đề (rollback của file lỗi không xóa khóa)
    (tmp_path / "course_1_en.json").write_text("{ không phải JSON", encoding="utf-8")
    bank = seed_review.load_bank(seed_review.DEFAULT_FILE)
    (tmp_path / "course_312_en.json").write_text(json.dumps(bank, ensure_ascii=False), encoding="utf-8")

    result = auto.seed_banks_if_empty(db_session, tmp_path)

    assert result["failed"] == ["course_1_en.json"] and result["loaded"] == ["course_312_en.json"]


def test_run_never_raises(monkeypatch):
    def boom():
        raise RuntimeError("database chưa sẵn sàng")

    assert auto.run(boom)["failed"] == ["*"]


def test_build_missing_embeddings_only_when_needed(db_session, course_312):
    calls = []

    def load_model():
        calls.append(1)
        return FakeModel()

    factory = session_factory(db_session)
    assert auto.build_missing_embeddings(factory, load_model) == 0 and calls == []  # chưa có đoạn nào → không nạp

    auto.seed_banks_if_empty(db_session)
    chunks = db_session.query(KnowledgeChunk).count()
    assert auto.build_missing_embeddings(factory, load_model) == chunks and len(calls) == 1
    assert auto.build_missing_embeddings(factory, load_model) == 0 and len(calls) == 1  # đủ vector → không nạp lại
    assert db_session.query(KnowledgeChunk).filter(KnowledgeChunk.embedding.is_(None)).count() == 0
