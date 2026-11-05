from fastapi import APIRouter, Depends
from app.core.dependencies import get_current_user
from app.models.user import Users
from app.schemas.user import UserMe

router = APIRouter()

@router.get("", response_model=UserMe, summary="Lấy hồ sơ người dùng đang đăng nhập")
def read_me(current_user: Users = Depends(get_current_user)):
    return current_user