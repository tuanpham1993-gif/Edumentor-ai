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

Lỗi: không thấy câu 404 · nội dung câu sai 422 (kèm danh sách lỗi) · mã trùng / sửa nhỏ sai / không bật được /
không duyệt được 409 · kỹ năng / đoạn tri thức sai 400.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_admin
from app.models.user import Users
from app.schemas.review_admin import (
    ApproveRequest,
    DeleteResultOut,
    EditResultOut,
    QuestionCreate,
    QuestionDetail,
    QuestionLevel,
    QuestionPage,
    QuestionType,
    QuestionUpdate,
    ReviewStatus,
    SuggestedCodeOut,
)
from app.services import review_admin_service as service
from app.services import review_bank_service as bank

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
