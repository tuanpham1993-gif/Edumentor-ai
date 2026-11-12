"""Router ôn tập (module 09 · Tuấn · GĐ2, 09/11/2026). Gắn vào api.py KHÔNG prefix (đường dẫn đầy đủ ở đây).

Mọi API cần đăng nhập (`get_current_user`); người dùng luôn lấy từ TOKEN.
Lượt làm bài của người khác → 404 như lượt không tồn tại (Q6 — không lộ lượt có tồn tại).

    GET   /api/courses/{course_id}/review            — thông tin ôn tập + lý do chưa thể ôn
    POST  /api/courses/{course_id}/review-attempts   — bắt đầu (có lượt dở → trả lại lượt đó)
    GET   /api/review-attempts/{attempt_id}          — đề + câu trả lời đã lưu (KHÔNG có đáp án)
    PATCH /api/review-attempts/{attempt_id}/answers  — lưu câu trả lời (Tạm rời / làm tiếp)
    POST  /api/review-attempts/{attempt_id}/submit   — nộp bài: chấm + (đạt lần đầu) Hoàn thành khóa (GĐ3)
    GET   /api/me/review-history                     — lịch sử các lượt đã nộp, lọc + phân trang (GĐ3)
    GET   /api/me/review-history/{attempt_id}        — chi tiết lượt đã nộp: đáp án đúng, điểm từng ý (GĐ3)
    GET   /api/admin/review-attempts/{attempt_id}/trace — vết RAG + prompt (chỉ admin — A4) (GĐ3)
"""

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    Query,
    Response,
    status,
)
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_admin
from app.core.email import send_review_result_email
from app.models.user import Users
from app.schemas.review import (
    AttemptOut,
    AttemptResultOut,
    AttemptTraceOut,
    HistoryPage,
    ReviewInfoOut,
    SaveAnswersRequest,
)
from app.services import course_gateway, review_service

router = APIRouter()

COURSE_NOT_FOUND = "Không tìm thấy khóa học."
ATTEMPT_NOT_FOUND = "Không tìm thấy bài ôn tập."


def _blocked(err: review_service.ReviewBlockedError) -> HTTPException:
    # Chưa / đã bỏ khóa → 403 (không có quyền ôn); chưa có ngân hàng → 409 (trạng thái chưa sẵn sàng).
    code = status.HTTP_409_CONFLICT if err.code == "no_question_bank" else status.HTTP_403_FORBIDDEN
    return HTTPException(status_code=code, detail=err.message)


@router.get(
    "/courses/{course_id}/review",
    response_model=ReviewInfoOut,
    summary="Thông tin ôn tập của khóa + lý do chưa thể ôn",
)
def read_review_info(
    course_id: int,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return review_service.review_info(db, current_user, course_id)
    except review_service.CourseNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, COURSE_NOT_FOUND) from None


@router.post(
    "/courses/{course_id}/review-attempts",
    response_model=AttemptOut,
    summary="Bắt đầu ôn tập (đang có lượt dở → trả lại lượt đó, resumed=true)",
)
def start_review(
    course_id: int,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return review_service.start_attempt(db, current_user, course_id)
    except review_service.CourseNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, COURSE_NOT_FOUND) from None
    except review_service.ReviewBlockedError as err:
        raise _blocked(err) from None


@router.get(
    "/review-attempts/{attempt_id}",
    response_model=AttemptOut,
    summary="Đề + câu trả lời đã lưu (không có đáp án / barem)",
)
def read_attempt(
    attempt_id: int,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return review_service.get_attempt(db, current_user, attempt_id)
    except review_service.AttemptNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, ATTEMPT_NOT_FOUND) from None


@router.patch(
    "/review-attempts/{attempt_id}/answers",
    response_model=AttemptOut,
    summary="Lưu câu trả lời (Tạm rời / làm tiếp) — gửi một phần hoặc tất cả",
)
def save_review_answers(
    attempt_id: int,
    request: SaveAnswersRequest,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return review_service.save_answers(db, current_user, attempt_id, request)
    except review_service.AttemptNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, ATTEMPT_NOT_FOUND) from None
    except review_service.AttemptLockedError:
        raise HTTPException(
            status.HTTP_409_CONFLICT, "Bài đã nộp — không sửa câu trả lời được nữa."
        ) from None
    except review_service.InvalidAnswerError as err:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, str(err)) from None


@router.post(
    "/review-attempts/{attempt_id}/submit",
    response_model=AttemptResultOut,
    summary="Nộp bài — chấm điểm; đạt lần đầu thì khóa Hoàn thành + kỹ năng \"Đã biết\"",
)
def submit_review(
    attempt_id: int,
    background_tasks: BackgroundTasks,
    response: Response,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        result = review_service.submit_attempt(
            db, current_user, attempt_id, schedule=background_tasks.add_task
        )
    except review_service.AttemptNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, ATTEMPT_NOT_FOUND) from None
    except review_service.AttemptLockedError:
        raise HTTPException(status.HTTP_409_CONFLICT, "Bài này đã được nộp.") from None
    except course_gateway.EnrollmentChangedError:
        # L1: khóa vừa đổi trạng thái (vd bỏ khóa) đúng lúc chấm → đã hủy lần nộp, bài vẫn đang làm
        raise HTTPException(
            status.HTTP_409_CONFLICT, "Trạng thái khóa học vừa thay đổi. Vui lòng nộp lại bài."
        ) from None
    if result["status"] == "grading":
        # T1: AI chấm quá thời gian → 202 "Đang chấm"; chấm nốt ở nền, xong thì có chuông + email.
        response.status_code = status.HTTP_202_ACCEPTED
        return result
    # Email gửi SAU khi trả kết quả (kết quả đã lưu xong) — lỗi gửi không ảnh hưởng bài làm.
    background_tasks.add_task(
        send_review_result_email,
        current_user.email,
        current_user.full_name,
        result["course_title"],
        result["score"],
        result["passed"],
        result["completed_course"],
        attempt_id,
    )
    return result


@router.get(
    "/me/review-history",
    response_model=HistoryPage,
    summary="Lịch sử ôn tập (lượt đã nộp) — lọc ?course_id=&passed=, phân trang",
)
def read_review_history(
    course_id: int | None = Query(None),
    passed: bool | None = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return review_service.history_list(
        db, current_user, course_id=course_id, passed=passed, page=page, size=size
    )


@router.get(
    "/me/review-history/{attempt_id}",
    response_model=AttemptResultOut,
    summary="Chi tiết lượt đã nộp: đáp án đúng, giải thích, điểm từng ý + bằng chứng",
)
def read_review_detail(
    attempt_id: int,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return review_service.history_detail(db, current_user, attempt_id)
    except review_service.AttemptNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, ATTEMPT_NOT_FOUND) from None


@router.get(
    "/admin/review-attempts/{attempt_id}/trace",
    response_model=AttemptTraceOut,
    summary="[Admin] Vết RAG + prompt + chấm của một lượt ôn tập",
)
def read_review_trace(
    attempt_id: int,
    _: Users = Depends(require_admin),
    db: Session = Depends(get_db),
):
    try:
        return review_service.attempt_trace(db, attempt_id)
    except review_service.AttemptNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, ATTEMPT_NOT_FOUND) from None
