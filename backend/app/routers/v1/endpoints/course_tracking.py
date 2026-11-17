"""Router /api/me/bookmarks, /api/me/courses, /api/courses/{id}/join.

Gắn vào `routers/v1/api.py` không prefix (khai đường dẫn đầy đủ ở đây).
Mọi endpoint đều yêu cầu đăng nhập (`get_current_user`); `user_id` luôn lấy từ token.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import Users
from app.schemas.common import PaginatedResponse
from app.schemas.course_tracking import (
    BookmarkCreateRequest,
    CourseJoinOut,
    CourseStatusOut,
    CourseStatusUpdateRequest,
    CourseTrackingItemOut,
    CourseTrackingStatus,
)
from app.schemas.user import MessageResponse
from app.services import course_tracking_service as service

router = APIRouter()

CurrentUser = Annotated[Users, Depends(get_current_user)]
DbSession = Annotated[Session, Depends(get_db)]


def _raise_http_error(err: service.CourseTrackingError) -> HTTPException:
    if isinstance(
        err,
        (
            service.CourseNotFoundError,
            service.TrackingNotFoundError,
            service.BookmarkNotFoundError,
        ),
    ):
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(err),
        )
    if isinstance(err, service.TrackingConflictError):
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(err),
        )
    if isinstance(err, service.ManualCompletionNotAllowedError):
        return HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(err),
        )
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=str(err),
    )


@router.post(
    "/me/bookmarks",
    response_model=CourseTrackingItemOut,
    status_code=status.HTTP_201_CREATED,
    summary="Lưu một khóa học để học sau (bookmarked)",
)
def create_bookmark(
    request: BookmarkCreateRequest,
    current_user: CurrentUser,
    db: DbSession,
):
    try:
        return service.add_bookmark(db, current_user, request.course_id)
    except service.CourseTrackingError as err:
        raise _raise_http_error(err) from None


@router.get(
    "/me/bookmarks",
    response_model=PaginatedResponse[CourseTrackingItemOut],
    summary="Lấy danh sách khóa học đã lưu",
)
def read_my_bookmarks(
    current_user: CurrentUser,
    db: DbSession,
    page: Annotated[int, Query(ge=1, description="Số trang (bắt đầu từ 1)")] = 1,
    page_size: Annotated[
        int, Query(ge=1, le=50, description="Số bản ghi mỗi trang (1-50)")
    ] = 10,
):
    return service.list_bookmarks(
        db,
        current_user,
        page=page,
        page_size=page_size,
    )


@router.delete(
    "/me/bookmarks/{course_id}",
    response_model=MessageResponse,
    summary="Xóa khóa học khỏi danh sách đã lưu (hard delete bản ghi bookmark)",
)
def delete_bookmark(
    course_id: int,
    current_user: CurrentUser,
    db: DbSession,
):
    try:
        service.remove_bookmark(db, current_user, course_id)
    except service.CourseTrackingError as err:
        raise _raise_http_error(err) from None
    return MessageResponse(message="Đã xóa khóa học khỏi danh sách đã lưu.")


@router.post(
    "/courses/{course_id}/join",
    response_model=CourseJoinOut,
    summary="Tham gia khóa học: ghi nhận ongoing (idempotent) và trả về URL bên ngoài",
)
def join_course(
    course_id: int,
    current_user: CurrentUser,
    db: DbSession,
):
    try:
        return service.join_course(db, current_user, course_id)
    except service.CourseTrackingError as err:
        raise _raise_http_error(err) from None


@router.get(
    "/me/courses",
    response_model=PaginatedResponse[CourseTrackingItemOut],
    summary="Lấy danh sách khóa học của tôi (?status=; mặc định loại trừ abandoned)",
)
def read_my_courses(
    current_user: CurrentUser,
    db: DbSession,
    status_filter: Annotated[
        CourseTrackingStatus | None,
        Query(
            alias="status",
            description="Lọc theo trạng thái (bookmarked | ongoing | completed | abandoned); bỏ trống để loại trừ abandoned",
        ),
    ] = None,
    page: Annotated[int, Query(ge=1, description="Số trang (bắt đầu từ 1)")] = 1,
    page_size: Annotated[
        int, Query(ge=1, le=50, description="Số bản ghi mỗi trang (1-50)")
    ] = 10,
):
    return service.list_my_courses(
        db,
        current_user,
        status_filter=status_filter,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/me/courses/{course_id}/status",
    response_model=CourseStatusOut,
    summary="Lấy trạng thái theo dõi hiện tại của người dùng đối với khóa học",
)
def read_my_course_status(
    course_id: int,
    current_user: CurrentUser,
    db: DbSession,
):
    try:
        return service.get_course_status(db, current_user, course_id)
    except service.CourseTrackingError as err:
        raise _raise_http_error(err) from None


@router.patch(
    "/me/courses/{course_id}/status",
    response_model=CourseTrackingItemOut,
    summary="Cập nhật trạng thái theo dõi sang trạng thái được phép",
)
def patch_my_course_status(
    course_id: int,
    request: CourseStatusUpdateRequest,
    current_user: CurrentUser,
    db: DbSession,
):
    try:
        return service.update_course_status(
            db,
            current_user,
            course_id,
            new_status=request.status,
        )
    except service.CourseTrackingError as err:
        raise _raise_http_error(err) from None


@router.delete(
    "/me/courses/{course_id}",
    response_model=CourseStatusOut,
    summary="Ngừng theo dõi khóa học (chuyển ongoing sang abandoned)",
)
def abandon_my_course(
    course_id: int,
    current_user: CurrentUser,
    db: DbSession,
):
    try:
        return service.abandon_course(db, current_user, course_id)
    except service.CourseTrackingError as err:
        raise _raise_http_error(err) from None
