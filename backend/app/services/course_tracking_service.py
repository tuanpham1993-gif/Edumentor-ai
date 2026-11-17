"""Nghiệp vụ Lưu khóa học và Theo dõi trạng thái học tập (`user_courses`).

Mỗi người dùng – mỗi khóa học có tối đa một bản ghi với 4 trạng thái:
  bookmarked -> ongoing (via /join hoặc PATCH) -> completed (chỉ qua module 09)
  ongoing <-> abandoned (bỏ theo dõi / học lại)

Thao tác có đụng tới kỹ năng hồ sơ (`add_learning_from_course`,
`remove_learning_from_course`) chạy trong cùng transaction với `user_courses`.
"""

from datetime import UTC, datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.user import Users
from app.models.user_course import UserCourse
from app.repositories import course_tracking_repository as repo
from app.services import user_skill_service

_ALLOWED_MANUAL_TRANSITIONS = {
    ("bookmarked", "ongoing"),
    ("abandoned", "ongoing"),
    ("ongoing", "abandoned"),
}


class CourseTrackingError(Exception):
    pass


class CourseNotFoundError(CourseTrackingError):
    """Không tìm thấy khóa học trong danh mục -> 404."""


class TrackingNotFoundError(CourseTrackingError):
    """Chưa có bản ghi theo dõi khóa học -> 404."""


class BookmarkNotFoundError(CourseTrackingError):
    """Khóa học không có trong danh sách đã lưu -> 404."""


class TrackingConflictError(CourseTrackingError):
    """Xung đột dữ liệu hoặc chuyển trạng thái không hợp lệ -> 409."""


class ManualCompletionNotAllowedError(CourseTrackingError):
    """Cố tình gửi trạng thái completed thủ công -> 422."""


def _to_tracking_item(row: UserCourse) -> dict:
    course = row.course
    return {
        "course_id": course.course_id,
        "title": course.title,
        "instructor": course.instructor,
        "organization": course.organization,
        "level": course.level,
        "rating": course.rating,
        "num_reviews": course.num_reviews,
        "url": course.url,
        "image": course.image,
        "skills_info": [
            {
                "skill_id": skill.skill_id,
                "skill": skill.skill,
                "is_active": skill.is_active,
            }
            for skill in course.skills_info
        ],
        "status": row.status,
        "joined_at": row.joined_at,
        "completed_at": row.completed_at,
        "created_at": row.created_at,
        "updated_at": row.updated_at,
    }


def _to_status_out(course_id: int, row: UserCourse | None) -> dict:
    if row is None:
        return {
            "course_id": course_id,
            "status": None,
            "is_bookmarked": False,
            "joined_at": None,
            "completed_at": None,
            "updated_at": None,
        }
    return {
        "course_id": course_id,
        "status": row.status,
        "is_bookmarked": row.status == "bookmarked",
        "joined_at": row.joined_at,
        "completed_at": row.completed_at,
        "updated_at": row.updated_at,
    }


def add_bookmark(db: Session, user: Users, course_id: int) -> dict:
    """POST /api/me/bookmarks — lưu khóa học để học sau."""
    course = repo.get_course(db, course_id)
    if course is None:
        raise CourseNotFoundError("Không tìm thấy khóa học.")

    row = repo.get_tracking(db, user.user_id, course_id, for_update=True)
    if row is None:
        repo.add_tracking(
            db,
            user_id=user.user_id,
            course_id=course_id,
            status="bookmarked",
        )
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise TrackingConflictError(
                "Khóa học này đã có trong danh sách theo dõi của bạn."
            ) from None
    elif row.status == "bookmarked":
        raise TrackingConflictError("Khóa học này đã có trong danh sách đã lưu.")
    elif row.status == "ongoing":
        raise TrackingConflictError(
            "Khóa học đang ở trạng thái đang học, không thể lưu bookmark."
        )
    elif row.status == "completed":
        raise TrackingConflictError("Khóa học đã hoàn thành, không thể lưu bookmark.")
    else:  # abandoned -> cho phép lưu lại để học sau
        row.status = "bookmarked"
        row.joined_at = None
        row.completed_at = None
        db.commit()

    loaded = repo.get_tracking_with_course(db, user.user_id, course_id)
    if loaded is None:
        raise CourseNotFoundError("Không tìm thấy khóa học.")
    return _to_tracking_item(loaded)


def list_bookmarks(
    db: Session,
    user: Users,
    *,
    page: int = 1,
    page_size: int = 10,
) -> dict:
    """GET /api/me/bookmarks — danh sách khóa học đã lưu."""
    total, rows = repo.list_by_user(
        db,
        user.user_id,
        status="bookmarked",
        page=page,
        page_size=page_size,
    )
    return {
        "items": [_to_tracking_item(row) for row in rows],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


def remove_bookmark(db: Session, user: Users, course_id: int) -> None:
    """DELETE /api/me/bookmarks/{course_id} — xóa cứng bản ghi bookmark."""
    course = repo.get_course(db, course_id)
    if course is None:
        raise CourseNotFoundError("Không tìm thấy khóa học.")

    row = repo.get_tracking(db, user.user_id, course_id, for_update=True)
    if row is None or row.status == "abandoned":
        raise BookmarkNotFoundError("Khóa học này không có trong danh sách đã lưu.")
    if row.status == "ongoing":
        raise TrackingConflictError(
            "Khóa học đang ở trạng thái đang học, không thể bỏ lưu bookmark. "
            "Hãy dùng DELETE /api/me/courses/{course_id} nếu muốn ngừng theo dõi."
        )
    if row.status == "completed":
        raise TrackingConflictError(
            "Khóa học đã hoàn thành, không thể bỏ lưu bookmark."
        )

    repo.delete_tracking(db, row)
    db.commit()


def join_course(db: Session, user: Users, course_id: int) -> dict:
    """POST /api/courses/{course_id}/join — idempotent (200 OK).

    - Đang ongoing hoặc completed -> giữ nguyên trạng thái & joined_at, trả url.
    - Chưa có / bookmarked / abandoned -> chuyển sang ongoing, cập nhật joined_at,
      và thêm kỹ năng đang bật của khóa vào hồ sơ dưới trạng thái learning.
    """
    course = repo.get_course(db, course_id)
    if course is None:
        raise CourseNotFoundError("Không tìm thấy khóa học.")

    row = repo.get_tracking(db, user.user_id, course_id, for_update=True)
    if row is not None and row.status in ("ongoing", "completed"):
        return {
            "course_id": course.course_id,
            "title": course.title,
            "status": row.status,
            "url": course.url,
            "joined_at": row.joined_at,
            "completed_at": row.completed_at,
            "updated_at": row.updated_at,
        }

    now = datetime.now(UTC)
    active_skill_ids = repo.get_active_course_skill_ids(db, course_id)

    if row is None:
        try:
            row = repo.add_tracking(
                db,
                user_id=user.user_id,
                course_id=course_id,
                status="ongoing",
                joined_at=now,
            )
            db.flush()
            user_skill_service.add_learning_from_course(
                db, user.user_id, active_skill_ids
            )
            db.commit()
        except IntegrityError:
            db.rollback()
            existing = repo.get_tracking(db, user.user_id, course_id, for_update=True)
            if existing is None:
                raise
            if existing.status in ("ongoing", "completed"):
                row = existing
            else:
                try:
                    existing.status = "ongoing"
                    existing.joined_at = now
                    existing.completed_at = None
                    user_skill_service.add_learning_from_course(
                        db, user.user_id, active_skill_ids
                    )
                    db.commit()
                    row = existing
                except Exception:
                    db.rollback()
                    raise
        except Exception:
            db.rollback()
            raise
    else:  # bookmarked hoặc abandoned
        try:
            row.status = "ongoing"
            row.joined_at = now
            row.completed_at = None
            user_skill_service.add_learning_from_course(
                db, user.user_id, active_skill_ids
            )
            db.commit()
        except Exception:
            db.rollback()
            raise

    db.refresh(row)
    return {
        "course_id": course.course_id,
        "title": course.title,
        "status": row.status,
        "url": course.url,
        "joined_at": row.joined_at,
        "completed_at": row.completed_at,
        "updated_at": row.updated_at,
    }


def list_my_courses(
    db: Session,
    user: Users,
    *,
    status_filter: str | None = None,
    page: int = 1,
    page_size: int = 10,
) -> dict:
    """GET /api/me/courses — mặc định loại trừ abandoned; ?status= lọc cụ thể."""
    if status_filter is None:
        total, rows = repo.list_by_user(
            db,
            user.user_id,
            exclude_statuses=("abandoned",),
            page=page,
            page_size=page_size,
        )
    else:
        total, rows = repo.list_by_user(
            db,
            user.user_id,
            status=status_filter,
            page=page,
            page_size=page_size,
        )
    return {
        "items": [_to_tracking_item(row) for row in rows],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


def get_course_status(db: Session, user: Users, course_id: int) -> dict:
    """GET /api/me/courses/{course_id}/status — trạng thái theo dõi hiện tại."""
    course = repo.get_course(db, course_id)
    if course is None:
        raise CourseNotFoundError("Không tìm thấy khóa học.")

    row = repo.get_tracking(db, user.user_id, course_id)
    return _to_status_out(course_id, row)


def update_course_status(
    db: Session,
    user: Users,
    course_id: int,
    *,
    new_status: str,
) -> dict:
    """PATCH /api/me/courses/{course_id}/status — chỉ cho phép luồng chuyển hợp lệ."""
    if new_status == "completed":
        raise ManualCompletionNotAllowedError(
            "Không thể tự đánh dấu trạng thái 'completed'. "
            "Khóa học chỉ hoàn thành khi bạn làm đạt bài ôn tập."
        )

    course = repo.get_course(db, course_id)
    if course is None:
        raise CourseNotFoundError("Không tìm thấy khóa học.")

    row = repo.get_tracking(db, user.user_id, course_id, for_update=True)
    if row is None:
        raise TrackingNotFoundError("Bạn chưa có bản ghi theo dõi cho khóa học này.")

    if row.status == "completed":
        raise TrackingConflictError(
            "Khóa học đã hoàn thành, không thể thay đổi trạng thái thủ công."
        )

    if (row.status, new_status) not in _ALLOWED_MANUAL_TRANSITIONS:
        raise TrackingConflictError(
            f"Không thể chuyển trạng thái khóa học từ '{row.status}' sang '{new_status}'."
        )

    active_skill_ids = repo.get_active_course_skill_ids(db, course_id)
    try:
        if new_status == "ongoing":
            row.status = "ongoing"
            row.joined_at = datetime.now(UTC)
            row.completed_at = None
            user_skill_service.add_learning_from_course(
                db, user.user_id, active_skill_ids
            )
        else:  # ("ongoing", "abandoned")
            keep_skill_ids = repo.get_other_ongoing_skill_ids(
                db, user.user_id, exclude_course_id=course_id
            )
            row.status = "abandoned"
            user_skill_service.remove_learning_from_course(
                db,
                user.user_id,
                active_skill_ids,
                keep_skill_ids=keep_skill_ids,
            )
        db.commit()
    except Exception:
        db.rollback()
        raise

    loaded = repo.get_tracking_with_course(db, user.user_id, course_id)
    if loaded is None:
        raise CourseNotFoundError("Không tìm thấy khóa học.")
    return _to_tracking_item(loaded)


def abandon_course(db: Session, user: Users, course_id: int) -> dict:
    """DELETE /api/me/courses/{course_id} — ngừng theo dõi (chuyển sang abandoned)."""
    course = repo.get_course(db, course_id)
    if course is None:
        raise CourseNotFoundError("Không tìm thấy khóa học.")

    row = repo.get_tracking(db, user.user_id, course_id, for_update=True)
    if row is None:
        raise TrackingNotFoundError("Bạn chưa theo dõi khóa học này.")

    if row.status == "bookmarked":
        raise TrackingConflictError(
            "Khóa học đang ở trạng thái đã lưu. "
            "Vui lòng dùng DELETE /api/me/bookmarks/{course_id} để bỏ lưu."
        )
    if row.status == "completed":
        raise TrackingConflictError("Khóa học đã hoàn thành, không thể ngừng theo dõi.")
    if row.status == "abandoned":
        raise TrackingConflictError(
            "Khóa học này đã ở trạng thái ngừng theo dõi trước đó."
        )

    active_skill_ids = repo.get_active_course_skill_ids(db, course_id)
    keep_skill_ids = repo.get_other_ongoing_skill_ids(
        db, user.user_id, exclude_course_id=course_id
    )
    try:
        row.status = "abandoned"
        user_skill_service.remove_learning_from_course(
            db,
            user.user_id,
            active_skill_ids,
            keep_skill_ids=keep_skill_ids,
        )
        db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(row)
    return _to_status_out(course_id, row)


# ─────────────── Hỗ trợ course_gateway (Module 09) ───────────────


def get_tracking_status_value(
    db: Session,
    user_id: int,
    course_id: int,
) -> str | None:
    row = repo.get_tracking(db, user_id, course_id)
    return row.status if row is not None else None


def mark_course_completed_in_tx(
    db: Session,
    user_id: int,
    course_id: int,
) -> None:
    """Đánh dấu khóa hoàn thành trong transaction do caller quản lý (CHỈ flush)."""
    row = repo.get_tracking(db, user_id, course_id, for_update=True)
    if row is not None and row.status == "ongoing":
        row.status = "completed"
        row.completed_at = datetime.now(UTC)
        db.flush()
