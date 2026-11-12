"""Router /api/me* — hồ sơ người dùng đang đăng nhập (module 01 · Tuấn · GĐ2–GĐ3, 05–06/11/2026).

Mọi API ở đây đều có `Depends(get_current_user)`: không token / token sai → 401,
và người dùng luôn được lấy từ TOKEN — không bao giờ nhận user_id từ client
(không xem/sửa được hồ sơ người khác — NFR-06).
Gắn vào app trong routers/v1/api.py với prefix "/me".

    GET   /api/me                  — xem hồ sơ
    PATCH /api/me                  — sửa họ tên (PATCH = sửa một phần)
    POST  /api/me/change-password  — đổi mật khẩu (POST = một hành động có kiểm tra)
    POST  /api/me/avatar           — đổi ảnh đại diện, multipart/form-data (GĐ7, 07/11)
    GET   /api/me/skills           — kỹ năng trong hồ sơ, lọc ?status=known|learning (GĐ4, 08/11)
    PATCH /api/me/skills           — thêm / đổi / gỡ nhiều kỹ năng trong MỘT lần lưu (GĐ4, 08/11)
    GET   /api/me/skills/suggestions — gợi ý kỹ năng cho ô "Thêm kỹ năng" (FĐ6, 08/11)
    GET   /api/me/skills/catalog/categories — danh mục kỹ năng + số lượng (FĐ6, 08/11)
    GET   /api/me/skills/catalog   — duyệt kỹ năng theo danh mục, phân trang (FĐ6, 08/11)
"""

from typing import Literal

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import Users
from app.schemas.user import (
    ChangePasswordRequest,
    MessageResponse,
    MeSummary,
    UpdateMeRequest,
    UserMe,
)
from app.schemas.user_skill import (
    SkillCatalogPage,
    SkillCategoryOut,
    SkillStatus,
    SkillSuggestionOut,
    UpdateSkillsRequest,
    UserSkillOut,
)
from app.services import user_service, user_skill_service
from app.utils import files, skill_categories

router = APIRouter()


@router.get("", response_model=UserMe, summary="Lấy hồ sơ người dùng đang đăng nhập")
def read_me(current_user: Users = Depends(get_current_user)):
    # get_current_user đã làm hết: đọc token, giải mã, tìm user → chỉ cần trả về.
    return current_user


@router.get("/summary", response_model=MeSummary, summary="4 ô thống kê trang Hồ sơ (khóa học, kỹ năng, lộ trình)")
def read_my_summary(
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return user_service.summary(db, current_user)


@router.patch("", response_model=UserMe, summary="Sửa họ tên + thông tin cá nhân (ngày sinh, giới tính, quê quán, SĐT, CCCD)")
def update_me(
    request: UpdateMeRequest,
    current_user: Users = Depends(get_current_user),
    # Cùng phiên DB với get_current_user (FastAPI chỉ gọi get_db một lần mỗi request).
    db: Session = Depends(get_db),
):
    details = {k: getattr(request, k) for k in request.model_fields_set if k != "full_name"}
    try:
        return user_service.update_profile(db, current_user, full_name=request.full_name, details=details)
    except user_service.CitizenIdTakenError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Số CCCD này đã được dùng cho một tài khoản khác.",
        ) from None


@router.post("/change-password", response_model=MessageResponse, summary="Đổi mật khẩu")
def change_password(
    request: ChangePasswordRequest,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        user_service.change_password(
            db,
            current_user,
            current_password=request.current_password,
            new_password=request.new_password,
        )
    except user_service.WrongCurrentPasswordError:
        # 400 chứ không phải 401: người dùng ĐÃ đăng nhập hợp lệ, chỉ nhập sai dữ liệu form.
        # Trả 401 có thể khiến frontend tưởng hết phiên và tự đăng xuất.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mật khẩu hiện tại không đúng.",
        ) from None
    except user_service.SamePasswordError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mật khẩu này đã được sử dụng.",
        ) from None
    return MessageResponse(message="Đổi mật khẩu thành công.")


@router.post("/avatar", response_model=UserMe, summary="Đổi ảnh đại diện")
def upload_avatar(
    file: UploadFile = File(...),
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Đọc tối đa MAX + 1 byte: đủ để biết "quá lớn" mà không phải đọc hết file khổng lồ vào RAM
    data = file.file.read(settings.AVATAR_MAX_BYTES + 1)
    try:
        return user_service.update_avatar(db, current_user, data=data)
    except files.FileTooLargeError:
        max_mb = settings.AVATAR_MAX_BYTES // (
            1024 * 1024
        )  # lấy từ cấu hình, không ghi cứng
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=f"Ảnh vượt quá {max_mb} MB.",
        ) from None
    except files.UnsupportedImageError:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Chỉ chấp nhận ảnh PNG hoặc JPEG.",
        ) from None


@router.get(
    "/skills",
    response_model=list[UserSkillOut],
    summary="Kỹ năng trong hồ sơ (lọc ?status=known|learning)",
)
def read_my_skills(
    # URL vẫn là ?status=… (alias), nhưng trong code đặt tên status_filter để KHÔNG che
    # module `status` của FastAPI (dùng cho mã lỗi ở các API khác trong file này).
    # None = lấy tất cả. Giá trị khác known/learning → FastAPI tự trả 422.
    status_filter: SkillStatus | None = Query(None, alias="status"),
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return user_skill_service.list_skills(db, current_user, status=status_filter)


@router.patch(
    "/skills",
    response_model=list[UserSkillOut],
    summary="Thêm / đổi trạng thái / gỡ kỹ năng — lưu tất cả một lần",
)
def update_my_skills(
    request: UpdateSkillsRequest,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return user_skill_service.update_skills(db, current_user, request)
    except user_skill_service.SkillNotInCatalogError as err:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Kỹ năng không có trong danh mục: {err.skill_ids}. Không có thay đổi nào được lưu.",
        ) from None
    except user_skill_service.SkillAlreadyInProfileError as err:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Kỹ năng đã có trong hồ sơ: {err.skill_ids}. Không có thay đổi nào được lưu.",
        ) from None
    except user_skill_service.SkillNotInProfileError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Kỹ năng không có trong hồ sơ: {err.skill_ids}. Không có thay đổi nào được lưu.",
        ) from None


@router.get(
    "/skills/suggestions",
    response_model=list[SkillSuggestionOut],
    summary="Gợi ý kỹ năng chưa có trong hồ sơ (học tiếp / liên quan / phổ biến)",
)
def suggest_my_skills(
    limit: int = Query(12, ge=1, le=30),
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return user_skill_service.suggest_skills(db, current_user, limit=limit)


@router.get(
    "/skills/catalog/categories",
    response_model=list[SkillCategoryOut],
    summary="Danh mục kỹ năng + số kỹ năng mỗi mục (trang Khám phá kỹ năng)",
)
def read_skill_categories(
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return user_skill_service.skill_categories_with_counts(db)


@router.get(
    "/skills/catalog",
    response_model=SkillCatalogPage,
    summary="Duyệt kỹ năng theo danh mục, tìm, sắp xếp, phân trang",
)
def browse_skill_catalog(
    category: str | None = Query(None, description="key danh mục; bỏ trống = tất cả"),
    q: str | None = Query(None, max_length=100, description="tìm trong tên kỹ năng"),
    sort: Literal["popular", "name"] = "popular",
    page: int = Query(1, ge=1),
    size: int = Query(24, ge=1, le=60),
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if category is not None and category not in skill_categories.KEYS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Danh mục không hợp lệ: {category}.",
        )
    return user_skill_service.browse_catalog(
        db, current_user, category=category, q=q, sort=sort, page=page, size=size
    )
