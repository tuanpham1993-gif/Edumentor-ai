"""Router /api/auth/* — đăng ký, đăng nhập (module 01 · Tuấn · GĐ2, 05/11/2026).

Lớp ROUTER = "lễ tân": nhận request (đã qua schema), gọi service, dịch kết quả/lỗi
sang mã HTTP. Không viết truy vấn hay quy tắc nghiệp vụ ở đây.
Gắn vào app trong routers/v1/api.py với prefix "/auth".
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.schemas.user import UserMe
from app.services import auth_service

router = APIRouter()


@router.post(
    "/register",
    # response_model: service trả object Users (có hashed_password) nhưng FastAPI CHỈ gửi
    # các trường có trong UserMe → lớp bảo vệ thứ hai chống lộ mật khẩu băm.
    response_model=UserMe,
    status_code=status.HTTP_201_CREATED,
    summary="Đăng ký tài khoản",
)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    # `request: RegisterRequest` → FastAPI tự đọc JSON và chạy mọi validator; sai → 422, hàm không chạy.
    try:
        return auth_service.register(
            db,
            email=request.email,
            full_name=request.full_name,
            password=request.password,  # không truyền confirm_password xuống
        )
    except auth_service.EmailAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,  # 409 = xung đột dữ liệu đã có
            detail="Email đã được sử dụng.",
        ) from None


@router.post("/login", response_model=TokenResponse, summary="Đăng nhập")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    result = auth_service.login(db, email=request.email, password=request.password)
    if result is None:
        # Cùng một thông báo cho mọi lý do (sai email / sai mật khẩu / bị khóa).
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email hoặc mật khẩu không đúng.",
        )
    token, user = result
    return TokenResponse(access_token=token, user=user)
