"""Rà bảo mật module 09 — mục 6.3 (module 09 · Tuấn · 18/11/2026).

Bổ sung cho các test sở hữu / khóa bài đã có (test_review_api, test_review_submit, test_review_grading_timeout):
    1. Trước khi nộp, mọi phản hồi cho học viên KHÔNG chứa đáp án đúng / barem / đáp án mẫu / thứ tự xáo gốc
       — kiểm cả TÊN TRƯỜNG lẫn NỘI DUNG chữ.
    2. MỌI API quản trị ôn tập: chưa đăng nhập 401, học viên 403.

Chạy:  python -m pytest tests/test_review_security.py -v      (trong thư mục backend)
"""

# ruff: noqa: F811 — fixture import từ test_review_api; pytest truyền qua TÊN tham số

import pytest

from app.models import ReviewAnswer
from tests.test_review_api import bank_312, start  # noqa: F401 — bank_312 là fixture

FORBIDDEN_KEYS = {
    "correct_index",
    "rubric",
    "explanation",
    "option_order",
    "question_id",
    "main_keywords",
    "sub_keywords",
    "rubric_result",
    "trace",
}


def all_keys(value) -> set[str]:
    if isinstance(value, dict):
        return set(value) | set().union(*(all_keys(v) for v in value.values()))
    if isinstance(value, list):
        return set().union(*(all_keys(v) for v in value)) if value else set()
    return set()


def secrets_of(db_session, attempt_id) -> list[str]:
    """Chữ không được lộ trước khi nộp: đáp án mẫu + từng ý barem (đủ dài để không trùng nhầm với đề)."""
    out = []
    for a in db_session.query(ReviewAnswer).filter_by(attempt_id=attempt_id):
        q = a.question
        if q.type == "essay":
            out += [r["text"] for r in q.rubric if len(r["text"]) > 25]
        if q.explanation and len(q.explanation) > 25:
            out.append(q.explanation)
    return out


def test_nothing_secret_before_submit(client, bank_312, student_headers, db_session):
    started = start(client, student_headers)
    attempt_id = started["attempt_id"]
    position = started["questions"][0]["position"]
    responses = {
        "start": started,
        "get": client.get(f"/api/review-attempts/{attempt_id}", headers=student_headers).json(),
        "save": client.patch(
            f"/api/review-attempts/{attempt_id}/answers",
            headers=student_headers,
            json={"answers": [{"position": position, "selected_index": 0}]},
        ).json(),
        "info": client.get("/api/courses/312/review", headers=student_headers).json(),
    }
    secrets = secrets_of(db_session, attempt_id)
    assert secrets  # có barem / đáp án mẫu để mà kiểm
    for name, body in responses.items():
        leaked = FORBIDDEN_KEYS & all_keys(body)
        assert not leaked, f"{name} lộ trường {leaked}"
        text = str(body)
        assert not [s for s in secrets if s in text], f"{name} lộ nội dung barem / đáp án mẫu"
    # Bài chưa nộp: không xem được trang kết quả (đáp án chỉ có sau khi nộp)
    assert client.get(f"/api/me/review-history/{attempt_id}", headers=student_headers).status_code == 404


ADMIN_CALLS = [
    ("get", "/api/admin/review/questions"),
    ("get", "/api/admin/review/questions/1"),
    ("post", "/api/admin/review/questions"),
    ("patch", "/api/admin/review/questions/1"),
    ("post", "/api/admin/review/questions/1/activate"),
    ("post", "/api/admin/review/questions/1/deactivate"),
    ("delete", "/api/admin/review/questions/1"),
    ("post", "/api/admin/review/questions/1/approve"),
    ("get", "/api/admin/review/questions/1/suggested-code"),
    ("post", "/api/admin/review/questions/1/reject"),
    ("get", "/api/admin/review/skills/1/suggested-code?type=mcq"),
    ("get", "/api/admin/review/skills/1/chunks"),
    ("get", "/api/admin/review/readiness"),
    ("get", "/api/admin/review/flags"),
    ("post", "/api/admin/review/flags/1/13/resolve"),
    ("get", "/api/admin/review-attempts/1/trace"),
]


@pytest.mark.parametrize(("method", "url"), ADMIN_CALLS)
def test_every_review_admin_api_blocks_guest_and_student(client, student_headers, method, url):
    call = getattr(client, method)
    body = {"json": {}} if method in ("post", "patch") else {}
    assert call(url, **body).status_code == 401
    assert call(url, headers=student_headers, **body).status_code == 403


def test_admin_call_list_covers_every_admin_route():
    """Thêm API quản trị mới mà quên thêm vào ADMIN_CALLS → test này báo."""
    from app.routers.v1.endpoints.admin import review_admin

    paths = {r.path for r in review_admin.router.routes}
    covered = {url.split("?")[0].replace("/api/admin/review", "") for _, url in ADMIN_CALLS}
    normalized = {
        p.replace("{question_id}", "1")
        .replace("{skill_id}", "1")
        .replace("{attempt_id}", "1")
        .replace("{position}", "13")
        for p in paths
    }
    assert normalized <= covered, f"Chưa kiểm phân quyền: {sorted(normalized - covered)}"
