"""Router /api/me* — hồ sơ người dùng đang đăng nhập (module 01 · Tuấn · GĐ2–GĐ3, 05–06/11/2026).

Mọi API ở đây đều có `Depends(get_current_user)`: không token / token sai → 401,
và người dùng luôn được lấy từ TOKEN — không bao giờ nhận user_id từ client
(không xem/sửa được hồ sơ người khác — NFR-06).
Gắn vào app trong routers/v1/api.py với prefix "/me".

    GET   /api/me                  — xem hồ sơ
    PATCH /api/me                  — sửa họ tên (PATCH = sửa một phần)
    POST  /api/me/change-password  — đổi mật khẩu (POST = một hành động có kiểm tra)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import Users
from app.schemas.user import (
    ChangePasswordRequest,
    MessageResponse,
    UpdateMeRequest,
    UserMe,
)
from app.services import user_service

router = APIRouter()


@router.get("", response_model=UserMe, summary="Lấy hồ sơ người dùng đang đăng nhập")
def read_me(current_user: Users = Depends(get_current_user)):
    # get_current_user đã làm hết: đọc token, giải mã, tìm user → chỉ cần trả về.
    return current_user


@router.patch("", response_model=UserMe, summary="Sửa họ tên")
def update_me(
    request: UpdateMeRequest,
    current_user: Users = Depends(get_current_user),
    # Cùng phiên DB với get_current_user (FastAPI chỉ gọi get_db một lần mỗi request).
    db: Session = Depends(get_db),
):
    return user_service.update_profile(db, current_user, full_name=request.full_name)


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
    return MessageResponse(message="Đổi mật khẩu thành công.")
