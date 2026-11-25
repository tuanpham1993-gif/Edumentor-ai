"""Router ôn tập (module 09 · Tuấn · GĐ2, 09/11/2026). Gắn vào api.py KHÔNG prefix (đường dẫn đầy đủ ở đây).

Mọi API cần đăng nhập (`get_current_user`); người dùng luôn lấy từ TOKEN.
Lượt làm bài của người khác → 404 như lượt không tồn tại (Q6 — không lộ lượt có tồn tại).

    GET   /api/courses/{course_id}/review            — thông tin ôn tập + lý do chưa thể ôn
    POST  /api/courses/{course_id}/review-attempts   — bắt đầu (có lượt dở → trả lại lượt đó)
    GET   /api/review-attempts/{attempt_id}          — đề + câu trả lời đã lưu (KHÔNG có đáp án)
    PATCH /api/review-attempts/{attempt_id}/answers  — lưu câu trả lời (Tạm rời / làm tiếp)
    DELETE /api/review-attempts/{attempt_id}         — bỏ bài làm dở: xóa hẳn, không điểm, không lịch sử (19/11)
    POST  /api/review-attempts/{attempt_id}/submit   — nộp bài: chấm + (đạt lần đầu) Hoàn thành khóa (GĐ3)
    GET   /api/me/review/skills?skill_ids=1,2,3      — kỹ năng → khóa ôn tập được (huy hiệu trên đồ thị, 20/11)
    GET   /api/me/review-history                     — lịch sử các lượt đã nộp, lọc + phân trang (GĐ3)
    GET   /api/me/review-history/{attempt_id}        — chi tiết lượt đã nộp: đáp án đúng, điểm từng ý (GĐ3)
    GET   /api/admin/review-attempts/{attempt_id}/trace — vết RAG + prompt (chỉ admin — A4) (GĐ3)
    GET   /api/skills/{skill_id}/review              — ôn theo KỸ NĂNG: thông tin + lý do chưa thể ôn (G2d, 22/11)
    POST  /api/skills/{skill_id}/review-attempts?path= — bắt đầu ôn theo kỹ năng (lượt dở → trả lại) (G2d);
                                                       thiếu câu → 202 {generation} AI soạn ở nền (G3d, 25/11)
    GET   /api/skills/{skill_id}/generation          — tiến độ việc AI soạn đề của kỹ năng (G3d)
      → làm bài / lưu / nộp / kết quả / lịch sử dùng chung các API /review-attempts/... ở trên.
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

from app.core import rate_limit as rl
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_admin
from app.core.email import send_review_result_email
from app.models.user import Users
from app.schemas.review import (
    AttemptOut,
    AttemptResultOut,
    AttemptTraceOut,
    GenerationOut,
    GenerationStartOut,
    HistoryPage,
    ReviewInfoOut,
    SaveAnswersRequest,
    SkillReviewInfoOut,
    SkillReviewsOut,
)
from app.services import course_gateway, review_service, skill_review_service

router = APIRouter()

COURSE_NOT_FOUND = "Không tìm thấy khóa học."
SKILL_NOT_FOUND = "Không tìm thấy kỹ năng."
PATH_NOT_FOUND = "Không tìm thấy lộ trình có kỹ năng này."
ATTEMPT_NOT_FOUND = "Không tìm thấy bài ôn tập."


def _blocked(err: review_service.ReviewBlockedError) -> HTTPException:
    # Chưa / đã bỏ khóa → 403 (không có quyền ôn); chưa có ngân hàng, đủ số bài dở → 409 (chưa sẵn sàng).
    conflict = ("no_question_bank", "too_many_unfinished")
    code = status.HTTP_409_CONFLICT if err.code in conflict else status.HTTP_403_FORBIDDEN
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
    "/skills/{skill_id}/review",
    response_model=SkillReviewInfoOut,
    summary="Ôn tập theo kỹ năng: thông tin + lý do chưa thể ôn (G2d)",
)
def read_skill_review_info(
    skill_id: int,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return skill_review_service.skill_review_info(db, current_user, skill_id)
    except skill_review_service.SkillNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, SKILL_NOT_FOUND) from None


@router.post(
    "/skills/{skill_id}/review-attempts",
    response_model=AttemptOut | GenerationStartOut,
    summary="Bắt đầu ôn theo kỹ năng (đang có lượt dở → trả lại, resumed=true). ?path= lộ trình đang mở. "
    "Thiếu câu → 202 {generation}: AI đang soạn đề ở nền (G3d)",
)
def start_skill_review(
    skill_id: int,
    response: Response,
    path: int | None = Query(default=None, ge=1, description="learning_paths.record_id — lộ trình của chính bạn"),
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return skill_review_service.start_skill_attempt(db, current_user, skill_id, path)
    except skill_review_service.GenerationPending as pending:
        response.status_code = status.HTTP_202_ACCEPTED
        return {"generation": pending.job}
    except skill_review_service.SkillNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, SKILL_NOT_FOUND) from None
    except skill_review_service.PathNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, PATH_NOT_FOUND) from None
    except skill_review_service.SkillBankMissingError as err:
        raise HTTPException(status.HTTP_409_CONFLICT, err.message) from None
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
        raise HTTPException(status.HTTP_409_CONFLICT, "Bài đã nộp — không sửa câu trả lời được nữa.") from None
    except review_service.InvalidAnswerError as err:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, str(err)) from None


@router.delete(
    "/review-attempts/{attempt_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Bỏ bài làm dở — xóa hẳn (không điểm, không vào lịch sử, không gọi AI)",
)
def abandon_review(
    attempt_id: int,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        review_service.abandon_attempt(db, current_user, attempt_id)
    except review_service.AttemptNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, ATTEMPT_NOT_FOUND) from None
    except review_service.AttemptLockedError:
        raise HTTPException(status.HTTP_409_CONFLICT, "Bài đã nộp — không bỏ được.") from None
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/review-attempts/{attempt_id}/submit",
    response_model=AttemptResultOut,
    summary='Nộp bài — chấm điểm; đạt lần đầu thì khóa Hoàn thành + kỹ năng "Đã biết"',
)
def submit_review(
    attempt_id: int,
    background_tasks: BackgroundTasks,
    response: Response,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # 19/11: ôn tập không giới hạn số lần, nhưng 2 lần nộp phải cách nhau ≥ REVIEW_SUBMIT_COOLDOWN giây (chặn công cụ
    # nộp tự động tốn lượt Gemini). Chỉ ĐẾM lần nộp thành công — nộp lỗi (404, 409…) không chấm nên không tính.
    rl.check_review_submit(current_user.user_id)
    try:
        result = review_service.submit_attempt(db, current_user, attempt_id, schedule=background_tasks.add_task)
    except review_service.AttemptNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, ATTEMPT_NOT_FOUND) from None
    except review_service.AttemptLockedError:
        raise HTTPException(status.HTTP_409_CONFLICT, "Bài này đã được nộp.") from None
    except course_gateway.EnrollmentChangedError:
        # L1: khóa vừa đổi trạng thái (vd bỏ khóa) đúng lúc chấm → đã hủy lần nộp, bài vẫn đang làm
        raise HTTPException(
            status.HTTP_409_CONFLICT, "Trạng thái khóa học vừa thay đổi. Vui lòng nộp lại bài."
        ) from None
    rl.record_review_submit(current_user.user_id)
    if result["status"] == "grading":
        # T1: AI chấm quá thời gian → 202 "Đang chấm"; chấm nốt ở nền, xong thì có chuông + email.
        response.status_code = status.HTTP_202_ACCEPTED
        return result
    # Email gửi SAU khi trả kết quả (kết quả đã lưu xong) — lỗi gửi không ảnh hưởng bài làm.
    title, target = review_service.email_target(result)
    background_tasks.add_task(
        send_review_result_email,
        current_user.email,
        current_user.full_name,
        title,
        result["score"],
        result["passed"],
        result["completed_course"],
        attempt_id,
        target=target,
    )
    return result


@router.get(
    "/me/review/skills",
    response_model=SkillReviewsOut,
    summary="Ôn tập trên đồ thị: mỗi kỹ năng → các khóa đã tham gia ôn tập được + lần làm gần nhất",
)
def read_skill_reviews(
    skill_ids: str = Query(..., description="Danh sách skill_id cách nhau bởi dấu phẩy, vd 1,2,3 (tối đa 100)"),
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        ids = [int(x) for x in skill_ids.split(",") if x.strip()]
    except ValueError:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT, "skill_ids phải là các số cách nhau bởi dấu phẩy."
        ) from None
    if len(ids) > review_service.MAX_SKILLS_PER_REQUEST:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT, f"Tối đa {review_service.MAX_SKILLS_PER_REQUEST} kỹ năng mỗi lần."
        )
    return review_service.skill_reviews(db, current_user, ids)


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
    return review_service.history_list(db, current_user, course_id=course_id, passed=passed, page=page, size=size)


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


@router.get(
    "/skills/{skill_id}/generation",
    response_model=GenerationOut,
    summary="Tiến độ việc AI soạn đề của kỹ năng (G3d) — 404 nếu chưa có việc nào",
)
def read_skill_generation(
    skill_id: int,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from app.services import review_generation_service

    try:
        info = skill_review_service.skill_readiness(db, skill_id)
    except skill_review_service.SkillNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, SKILL_NOT_FOUND) from None
    job = review_generation_service.latest_job(db, info.bank_skill_id)
    if job is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Chưa có việc soạn đề nào cho kỹ năng này.")
    return review_generation_service.job_view(job)
