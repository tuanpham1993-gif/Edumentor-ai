"""G1 — tìm kỹ năng theo tên → skill_id (module 09 · Tuấn · 21/11/2026 — docs/Review-Skill-Search.md).

Embedder giả (không tải mô hình): mỗi tên ↦ vector cố định; truy vấn tiếng Việt ↦ gần vector tên tiếng Anh tương ứng.
Chạy:  python -m pytest tests/test_skill_search.py -v      (trong thư mục backend)
"""

import numpy as np
import pytest

from app.ai.review.bm25 import BM25, tokenize
from app.ai.review.pipeline import skill_search as ss
from app.models import ReviewQuestion, Skills
from app.services import skill_search_service as svc

SKILLS = [
    (4, "JavaScript"),
    (199, "Java"),
    (877, "javascript syntax"),
    (2283, "JavaScript (Programming Language)"),
    (4919, "Javascript"),
    (4406, "ZOWE"),
    (167, "Python Programming"),
    (5852, "Python programming"),
    (4853, "If Statements"),
    (4852, "Loops"),
    (23, "Communication"),
]
DIM = len(SKILLS) + 2
# truy vấn tiếng Việt / mô tả → tên tiếng Anh mà "mô hình" coi là gần nghĩa
MEANING = {"lập trình python": "Python Programming", "giao tiếp": "Communication", "vòng lặp": "Loops", "java": "ZOWE"}


def vec_for(text: str) -> np.ndarray:
    names = [n for _, n in SKILLS]
    target = MEANING.get(text.lower(), text)
    v = np.zeros(DIM, dtype=np.float32)
    hits = [i for i, n in enumerate(names) if ss.normalize(n) == ss.normalize(target)]
    for i in hits:
        v[i] = 1.0
    if not hits:
        v[-1] = 1.0  # không giống tên nào
    return v / np.linalg.norm(v)


def index(with_vectors=True):
    vectors = np.stack([vec_for(n) for _, n in SKILLS]) if with_vectors else None
    return ss.SkillIndex.build(SKILLS, vectors)


def run(q, *, limit=5, counts=None, with_vectors=True):
    ctx = ss.SearchCtx(query=q, index=index(with_vectors), limit=limit, embed=lambda t: vec_for(t).tolist(),
                       counts=lambda ids: counts or {})  # fmt: skip
    return ss.run(ctx)


# ─────────────── Khối nhỏ ───────────────


def test_normalize_drops_brackets_case_and_punctuation():
    assert ss.normalize("JavaScript (Programming Language)") == "javascript"
    assert ss.normalize("  React.js ") == "react js"
    assert ss.normalize("C++") == "c++" and ss.normalize("C#") == "c#"


def test_bm25_ranks_exact_token_first():
    bm = BM25([tokenize("java"), tokenize("java ee"), tokenize("javascript")])
    top = bm.top(["java"], 5)
    assert [i for i, _ in top] == [0, 1]  # "javascript" không chứa token "java"


# ─────────────── Pipeline ───────────────


def test_short_word_java_is_exact_not_vector_noise():
    ctx = run("java")
    assert ctx.confident and ctx.results[0]["skill_id"] == 199 and ctx.results[0]["match"] == "exact"
    assert ctx.results[0]["skill"] == "Java"  # ZOWE (vector "nhầm") không lên đầu


def test_duplicate_names_are_grouped_and_bank_skill_represents_group():
    ctx = run("javascript", counts={4919: (20, 0)})  # #4919 có ngân hàng câu hỏi
    top = ctx.results[0]
    assert top["skill_id"] == 4919 and top["active_questions"] == 20
    assert {a["skill_id"] for a in top["aliases"]} == {4, 2283}  # gom 3 tên trùng


def test_vietnamese_query_found_by_meaning_but_not_auto_picked_when_close():
    ctx = run("lập trình python", counts={167: (41, 2)})
    top = ctx.results[0]
    assert top["skill_id"] == 167 and top["match"] == "hybrid" and top["pending_questions"] == 2  # "python" khớp cả chữ
    assert [a["skill_id"] for a in top["aliases"]] == [5852]


def test_keyword_catches_if_else_that_vector_misses():
    ctx = run("if else")
    assert ctx.results[0]["skill_id"] == 4853 and ctx.results[0]["match"] == "keyword"
    assert ctx.confident is False  # không khớp nguyên văn, không có vector gần → để người dùng chọn


def test_typo_is_corrected():
    ctx = run("pyhton programing", with_vectors=False)
    assert ctx.results[0]["skill_id"] in (167, 5852)
    keyword = next(t for t in ctx.trace if t["node"] == "3_keyword")
    assert keyword["output"]["typo"] == {"pyhton": "python", "programing": "programming"}


def test_unknown_query_is_never_confident():
    assert run("nấu ăn món Huế").confident is False


def test_works_without_vectors():
    ctx = run("java", with_vectors=False)
    assert ctx.results[0]["skill_id"] == 199
    vector = next(t for t in ctx.trace if t["node"] == "4_vector")
    assert "skipped" in vector["output"]


def test_empty_query_returns_nothing():
    for q in ("", "   ", "()"):
        ctx = run(q)
        assert ctx.results == [] and ctx.confident is False


def test_limit_and_trace_has_every_block():
    ctx = run("javascript", limit=2)
    assert len(ctx.results) == 2
    assert [t["node"] for t in ctx.trace] == [n.name for n in ss.NODES]


# ─────────────── Service + API ───────────────


@pytest.fixture()
def skills_db(db_session):
    for skill_id, name in SKILLS:
        db_session.add(Skills(skill_id=skill_id, skill=name, is_active=True))
    db_session.add(Skills(skill_id=9999, skill="Java Hidden", is_active=False))  # ngừng dùng → không tìm
    db_session.flush()
    svc._state.update(index=None, built=0.0, signature=None)
    yield db_session
    svc._state.update(index=None, built=0.0, signature=None)


def test_service_counts_active_questions_and_skips_inactive_skills(skills_db, monkeypatch):
    monkeypatch.setattr(svc, "load_vectors", lambda sig, path=None: None)
    for i in range(3):
        skills_db.add(ReviewQuestion(skill_id=199, type="mcq", level="recognize", content=f"Q{i}",
                                     options=["a", "b", "c", "d"], correct_index=0, is_active=True))  # fmt: skip
    skills_db.flush()

    out = svc.search(skills_db, "java", embed=lambda t: None)

    assert out["confident"] and out["results"][0]["skill_id"] == 199 and out["results"][0]["active_questions"] == 3
    assert all(r["skill_id"] != 9999 for r in out["results"])


def test_vector_cache_roundtrip_and_signature(tmp_path):
    rows = SKILLS[:3]
    path = tmp_path / "v.npz"
    assert svc.build_vectors(rows, lambda names: np.eye(3, 4, dtype=np.float32), path) == 3
    assert svc.load_vectors(svc.signature(rows), path).shape == (3, 4)
    assert svc.load_vectors(svc.signature(rows[:2]), path) is None  # danh sách kỹ năng đổi → không dùng cache cũ


def test_api_requires_admin_and_returns_matches(client, skills_db, admin_headers, student_headers, monkeypatch):
    monkeypatch.setattr(svc, "load_vectors", lambda sig, path=None: None)
    monkeypatch.setattr(svc, "_embed", lambda t: None)
    url = "/api/admin/review/skills/search"

    assert client.get(url, params={"q": "java"}).status_code == 401
    assert client.get(url, params={"q": "java"}, headers=student_headers).status_code == 403
    assert client.get(url, params={"q": ""}, headers=admin_headers).status_code == 422

    body = client.get(url, params={"q": "java", "limit": 3}, headers=admin_headers).json()
    assert body["confident"] is True and body["results"][0]["skill"] == "Java"
    assert len(body["results"]) <= 3 and "trace" not in body
