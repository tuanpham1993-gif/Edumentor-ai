"""Router quản trị ngân hàng câu hỏi ôn tập (module 09 · Tuấn · GĐ7 bước 7.3, 13/11/2026).

Gắn trong api.py với prefix "/admin/review" (không dùng /api/admin/questions của BA để khỏi đụng router admin của Khôi).
Mọi API chỉ admin (`require_admin`: chưa đăng nhập 401, học viên 403).

    GET    /api/admin/review/questions                 — danh sách: lọc + tìm + phân trang
    GET    /api/admin/review/questions/{id}            — chi tiết + đáp án / barem + lịch sử phiên bản
    POST   /api/admin/review/questions                 — thêm câu (phiên bản 1, đã duyệt, bật)
    PATCH  /api/admin/review/questions/{id}            — sửa: tại chỗ hoặc tạo phiên bản mới (QT2) / "Sửa nhỏ" (QT5)
    POST   /api/admin/review/questions/{id}/activate   — bật
    POST   /api/admin/review/questions/{id}/deactivate — tắt
    DELETE /api/admin/review/questions/{id}            — chưa ai làm → xóa thật; đã làm → chỉ tắt
    POST   /api/admin/review/questions/{id}/approve    — duyệt câu AI soạn + bật (QT6); không gửi mã → tự cấp mã gợi ý
    GET    /api/admin/review/questions/{id}/suggested-code — mã gợi ý điền sẵn khi duyệt (vd VAR-TN-15)
    POST   /api/admin/review/questions/{id}/reject     — từ chối câu AI soạn (ẩn, không xóa)
    GET    /api/admin/review/skills/{skill_id}/suggested-code?type= — mã gợi ý cho câu sắp thêm (7.6 P3)
    GET    /api/admin/review/skills/{skill_id}/chunks  — đoạn tri thức của kỹ năng (ô chọn khi sửa câu, 7.6)
    GET    /api/admin/review/skills/search?q=&limit=    — tìm kỹ năng theo tên (G1, 21/11): exact + BM25 + vector, RRF
    GET    /api/admin/review/skill-scopes               — phạm vi ôn tập theo kỹ năng: lọc label / category / source / q (G3.0)
    PATCH  /api/admin/review/skill-scopes/{skill_id}    — admin đặt nhãn Mở / Không mở / Chưa rõ (G3.0, 24/11)
    GET    /api/admin/review/readiness                 — mức sẵn sàng ôn tập từng khóa (7.4, 16/11); ?course_id= → 1 khóa
    GET    /api/admin/review/flags                     — bài cần xem lại: câu tự luận bị gắn cờ (17/11)
    POST   /api/admin/review/flags/{attempt_id}/{position}/resolve — admin chấm lại từng ý (Đạt / Không đạt)

Lỗi: không thấy câu 404 · nội dung câu sai 422 (kèm danh sách lỗi) · mã trùng / sửa nhỏ sai / không bật được /
không duyệt được 409 · kỹ năng / đoạn tri thức sai 400.
"""

from typing import Literal

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_admin
from app.core.email import send_review_result_email
from app.models.user import Users
from app.repositories import review_repository as repo
from app.schemas.review_admin import (
    ApproveRequest,
    ChunkOut,
    DeleteResultOut,
    EditResultOut,
    FlagPageOut,
    FlagReason,
    FlagResolveOut,
    FlagResolveRequest,
    QuestionCreate,
    QuestionDetail,
    QuestionLevel,
    QuestionPage,
    QuestionType,
    QuestionUpdate,
    ReadinessOut,
    ReviewStatus,
    ScopeCategory,
    ScopeLabel,
    SkillScopeOut,
    SkillScopePage,
    SkillScopeUpdate,
    SkillSearchOut,
    SuggestedCodeOut,
)
from app.services import review_admin_service as service
from app.services import review_bank_service as bank
from app.services import review_flag_service as flags
from app.services import review_readiness_service as readiness_service
from app.services import review_service, skill_scope_service, skill_search_service

router = APIRouter()

QUESTION_NOT_FOUND = "Không tìm thấy câu hỏi."


def _http(err: Exception) -> HTTPException:
    """Đổi lỗi nghiệp vụ thành HTTPException (thứ tự: lớp con trước lớp cha BankError)."""
    if isinstance(err, service.QuestionNotFoundError):
        return HTTPException(status.HTTP_404_NOT_FOUND, QUESTION_NOT_FOUND)
    if isinstance(err, bank.QuestionInvalidError):
        # 422 viết số: hằng HTTP_422_UNPROCESSABLE_ENTITY đã bị Starlette đánh dấu bỏ
        return HTTPException(422, {"message": "Câu hỏi không hợp lệ", "errors": err.errors})
    if isinstance(
        err,
        (
            service.DuplicateCodeError,
            service.ApprovalNotAllowedError,
            bank.MinorEditNotAllowedError,
            bank.ActivationNotAllowedError,
        ),
    ):
        return HTTPException(status.HTTP_409_CONFLICT, str(err))
    return HTTPException(status.HTTP_400_BAD_REQUEST, str(err))  # InvalidReferenceError, BankError khác


ERRORS = (service.QuestionNotFoundError, bank.BankError)


@router.get(
    "/questions",
    response_model=QuestionPage,
    summary="[Admin] Danh sách câu hỏi ôn tập",
)
def list_questions(
    course_id: int | None = None,
    skill_id: int | None = None,
    type: QuestionType | None = None,
    level: QuestionLevel | None = None,
    source: str | None = Query(default=None, pattern="^(bank|ai)$"),
    is_active: bool | None = None,
    review_status: ReviewStatus | None = None,
    q: str | None = Query(default=None, max_length=200, description="Tìm trong nội dung / mã câu"),
    latest_only: bool = Query(default=True, description="Chỉ phiên bản mới nhất của mỗi câu"),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    _: Users = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return service.list_questions(
        db,
        course_id=course_id,
        skill_id=skill_id,
        type=type,
        level=level,
        source=source,
        is_active=is_active,
        review_status=review_status,
        q=q,
        latest_only=latest_only,
        page=page,
        size=size,
    )


@router.get(
    "/questions/{question_id}",
    response_model=QuestionDetail,
    summary="[Admin] Chi tiết câu hỏi + lịch sử phiên bản",
)
def read_question(question_id: int, _: Users = Depends(require_admin), db: Session = Depends(get_db)):
    try:
        return service.get_detail(db, question_id)
    except ERRORS as err:
        raise _http(err) from None


@router.post(
    "/questions",
    response_model=QuestionDetail,
    status_code=status.HTTP_201_CREATED,
    summary="[Admin] Thêm câu hỏi",
)
def create_question(
    body: QuestionCreate,
    admin: Users = Depends(require_admin),
    db: Session = Depends(get_db),
):
    try:
        return service.create(db, body, admin.user_id)
    except ERRORS as err:
        raise _http(err) from None


@router.patch(
    "/questions/{question_id}",
    response_model=EditResultOut,
    summary="[Admin] Sửa câu hỏi (tự tạo phiên bản mới nếu câu đã có bài làm)",
)
def update_question(
    question_id: int,
    body: QuestionUpdate,
    admin: Users = Depends(require_admin),
    db: Session = Depends(get_db),
):
    try:
        return service.update(db, question_id, body, admin.user_id)
    except ERRORS as err:
        raise _http(err) from None


@router.post(
    "/questions/{question_id}/activate",
    response_model=QuestionDetail,
    summary="[Admin] Bật câu hỏi",
)
def activate_question(question_id: int, _: Users = Depends(require_admin), db: Session = Depends(get_db)):
    try:
        return service.set_active(db, question_id, True)
    except ERRORS as err:
        raise _http(err) from None


@router.post(
    "/questions/{question_id}/deactivate",
    response_model=QuestionDetail,
    summary="[Admin] Tắt câu hỏi",
)
def deactivate_question(question_id: int, _: Users = Depends(require_admin), db: Session = Depends(get_db)):
    try:
        return service.set_active(db, question_id, False)
    except ERRORS as err:
        raise _http(err) from None


@router.delete(
    "/questions/{question_id}",
    response_model=DeleteResultOut,
    summary="[Admin] Xóa câu hỏi (đã có bài làm → chỉ tắt)",
)
def delete_question(question_id: int, _: Users = Depends(require_admin), db: Session = Depends(get_db)):
    try:
        return service.delete(db, question_id)
    except ERRORS as err:
        raise _http(err) from None


@router.post(
    "/questions/{question_id}/approve",
    response_model=QuestionDetail,
    summary="[Admin] Duyệt câu AI soạn",
)
def approve_question(
    question_id: int,
    body: ApproveRequest | None = None,
    admin: Users = Depends(require_admin),
    db: Session = Depends(get_db),
):
    try:
        return service.approve(db, question_id, body or ApproveRequest(), admin.user_id)
    except ERRORS as err:
        raise _http(err) from None


@router.get(
    "/questions/{question_id}/suggested-code",
    response_model=SuggestedCodeOut,
    summary="[Admin] Mã gợi ý khi duyệt (vd VAR-TN-15)",
)
def suggested_code(question_id: int, _: Users = Depends(require_admin), db: Session = Depends(get_db)):
    try:
        return service.suggest_code(db, question_id)
    except ERRORS as err:
        raise _http(err) from None


@router.post(
    "/questions/{question_id}/reject",
    response_model=QuestionDetail,
    summary="[Admin] Từ chối câu AI soạn",
)
def reject_question(
    question_id: int,
    admin: Users = Depends(require_admin),
    db: Session = Depends(get_db),
):
    try:
        return service.reject(db, question_id, admin.user_id)
    except ERRORS as err:
        raise _http(err) from None


@router.get(
    "/readiness",
    response_model=ReadinessOut,
    summary="[Admin] Mức sẵn sàng ôn tập của khóa (đủ câu để ráp đề chưa)",
)
def read_readiness(
    course_id: int | None = None,
    _: Users = Depends(require_admin),
    db: Session = Depends(get_db),
):
    try:
        return readiness_service.readiness(db, course_id)
    except readiness_service.CourseNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Không tìm thấy khóa học.") from None


@router.get(
    "/skills/{skill_id}/chunks",
    response_model=list[ChunkOut],
    summary="[Admin] Đoạn tri thức của kỹ năng",
)
def list_skill_chunks(skill_id: int, _: Users = Depends(require_admin), db: Session = Depends(get_db)):
    if not repo.skill_exists(db, skill_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Không tìm thấy kỹ năng.")
    return repo.chunks_for_skill(db, skill_id)


@router.get(
    "/skills/{skill_id}/suggested-code",
    response_model=SuggestedCodeOut,
    summary="[Admin] Mã gợi ý cho câu sắp thêm của kỹ năng",
)
def skill_suggested_code(
    skill_id: int,
    type: QuestionType,
    _: Users = Depends(require_admin),
    db: Session = Depends(get_db),
):
    try:
        return service.suggest_code_for_skill(db, skill_id, type)
    except service.InvalidReferenceError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Không tìm thấy kỹ năng.") from None


# ─────────────── Bài cần xem lại (17/11/2026) ───────────────


@router.get("/flags", response_model=FlagPageOut, summary="[Admin] Câu tự luận cần xem lại")
def list_flags(
    status_: str = Query("open", alias="status", pattern="^(open|resolved|all)$"),
    reason: FlagReason | None = None,
    course_id: int | None = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    _: Users = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return flags.list_flags(db, status=status_, reason=reason, course_id=course_id, page=page, size=size)


@router.post(
    "/flags/{attempt_id}/{position}/resolve",
    response_model=FlagResolveOut,
    summary="[Admin] Chấm lại một câu tự luận: Đạt / Không đạt từng ý",
)
def resolve_flag(
    attempt_id: int,
    position: int,
    body: FlagResolveRequest,
    background_tasks: BackgroundTasks,
    admin: Users = Depends(require_admin),
    db: Session = Depends(get_db),
):
    try:
        result = flags.resolve(db, attempt_id, position, body.labels, admin, body.note)
    except flags.FlagNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Không tìm thấy câu tự luận này.") from None
    except flags.FlagConflictError as err:
        raise HTTPException(status.HTTP_409_CONFLICT, str(err)) from None
    except flags.FlagInvalidError as err:
        raise HTTPException(422, str(err)) from None
    if result["notify_email"]:  # đổi sang Đạt → email kết quả, dùng chung mẫu khi nộp bài (Tuấn chốt 17/11)
        item = result["item"]
        title, target = review_service.email_target(item)
        background_tasks.add_task(
            send_review_result_email,
            item["user_email"],
            item["user_name"],
            title,
            item["attempt_score"],
            item["attempt_passed"],
            result["completed_course"],
            attempt_id,
            target=target,
        )
    return result


# ─────────────── Tìm kỹ năng theo tên (G1, 21/11/2026) ───────────────


@router.get("/skills/search", response_model=SkillSearchOut, summary="[Admin] Tìm kỹ năng theo tên → skill_id")
def search_skills(
    q: str = Query(..., min_length=1, max_length=100, description="Tên kỹ năng, tiếng Anh hoặc tiếng Việt"),
    limit: int = Query(5, ge=1, le=20),
    _: Users = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return skill_search_service.search(db, q, limit)


# ─────────────── Phạm vi ôn tập theo kỹ năng (G3.0, 24/11/2026) ───────────────


@router.get(
    "/skill-scopes", response_model=SkillScopePage, summary="[Admin] Phạm vi ôn tập theo kỹ năng (nhãn AI / admin)"
)
def list_skill_scopes(
    label: ScopeLabel | Literal["unlabeled"] | None = None,
    category: ScopeCategory | None = None,
    source: Literal["ai", "admin"] | None = None,
    q: str | None = Query(None, max_length=100, description="Tìm trong tên kỹ năng"),
    skill_id: int | None = Query(None, ge=1),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    _: Users = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return skill_scope_service.list_page(
        db, label=label, category=category, source=source, q=q, skill_id=skill_id, page=page, size=size
    )


@router.patch("/skill-scopes/{skill_id}", response_model=SkillScopeOut, summary="[Admin] Đặt nhãn phạm vi cho kỹ năng")
def update_skill_scope(
    skill_id: int,
    body: SkillScopeUpdate,
    admin: Users = Depends(require_admin),
    db: Session = Depends(get_db),
):
    try:
        return skill_scope_service.set_scope(
            db, admin, skill_id, label=body.label, category=body.category, reason=body.reason
        )
    except skill_scope_service.ScopeSkillNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Không tìm thấy kỹ năng.") from None
