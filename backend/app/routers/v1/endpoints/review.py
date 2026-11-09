"""Router ôn tập (module 09 · Tuấn · GĐ2, 09/11/2026). Gắn vào api.py KHÔNG prefix (đường dẫn đầy đủ ở đây).

Mọi API cần đăng nhập (`get_current_user`); người dùng luôn lấy từ TOKEN.
Lượt làm bài của người khác → 404 như lượt không tồn tại (Q6 — không lộ lượt có tồn tại).

    GET   /api/courses/{course_id}/review            — thông tin ôn tập + lý do chưa thể ôn
    POST  /api/courses/{course_id}/review-attempts   — bắt đầu (có lượt dở → trả lại lượt đó)
    GET   /api/review-attempts/{attempt_id}          — đề + câu trả lời đã lưu (KHÔNG có đáp án)
    PATCH /api/review-attempts/{attempt_id}/answers  — lưu câu trả lời (Tạm rời / làm tiếp)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import Users
from app.schemas.review import AttemptOut, ReviewInfoOut, SaveAnswersRequest
from app.services import review_service

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
