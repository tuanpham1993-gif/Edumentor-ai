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
    return current_user


@router.patch("", response_model=UserMe, summary="Sửa họ tên")
def update_me(
    request: UpdateMeRequest,
    current_user: Users = Depends(get_current_user),
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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mật khẩu hiện tại không đúng.",
        ) from None
    return MessageResponse(message="Đổi mật khẩu thành công.")
