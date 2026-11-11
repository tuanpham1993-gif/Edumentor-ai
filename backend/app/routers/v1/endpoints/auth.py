"""Router /api/auth/* (module 01 · Tuấn).

- GĐ2 (05/11/2026): đăng ký, đăng nhập.
- GĐ5 (06/11/2026): quên mật khẩu, đặt lại mật khẩu.
- GĐ6 (07/11/2026): làm mới access token (refresh), đăng xuất.

Lớp ROUTER = "lễ tân": nhận request (đã qua schema), gọi service, dịch kết quả/lỗi
sang mã HTTP. Không viết truy vấn hay quy tắc nghiệp vụ ở đây.
Gắn vào app trong routers/v1/api.py với prefix "/auth".
"""

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.email import send_password_reset_email
from app.schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    RefreshRequest,
    RefreshResponse,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
)
from app.schemas.user import MessageResponse, UserMe
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
    access_token, refresh_token, user = result
    return TokenResponse(
        access_token=access_token, refresh_token=refresh_token, user=user
    )


# Luôn cùng một câu dù email có hay không → không lộ email nào đã đăng ký (FR-47).
FORGOT_PASSWORD_MESSAGE = (
    "Nếu email đã được đăng ký, chúng tôi đã gửi liên kết đặt lại mật khẩu."
)


@router.post(
    "/forgot-password", response_model=MessageResponse, summary="Quên mật khẩu"
)
def forgot_password(
    request: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    token = auth_service.forgot_password(db, email=request.email)
    if token is not None:
        # Gửi email ở NỀN, sau khi đã trả response → mọi request phản hồi nhanh như nhau,
        # không dò được email có tồn tại qua thời gian phản hồi.
        background_tasks.add_task(send_password_reset_email, request.email, token)
    return MessageResponse(message=FORGOT_PASSWORD_MESSAGE)


@router.post(
    "/reset-password", response_model=MessageResponse, summary="Đặt lại mật khẩu"
)
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    try:
        auth_service.reset_password(
            db, token=request.token, new_password=request.new_password
        )
    except auth_service.InvalidResetTokenError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Liên kết đặt lại mật khẩu không hợp lệ hoặc đã hết hạn.",
        ) from None
    return MessageResponse(message="Đặt lại mật khẩu thành công.")


@router.post("/refresh", response_model=RefreshResponse, summary="Làm mới access token")
def refresh_token(request: RefreshRequest, db: Session = Depends(get_db)):
    try:
        access, new_refresh = auth_service.refresh(
            db, refresh_token=request.refresh_token
        )
    except auth_service.InvalidRefreshTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.",
        ) from None
    return RefreshResponse(access_token=access, refresh_token=new_refresh)


@router.post("/logout", response_model=MessageResponse, summary="Đăng xuất")
def logout(request: RefreshRequest, db: Session = Depends(get_db)):
    # Không bắt buộc access token: người dùng hay đăng xuất khi access đã hết hạn.
    # Luôn 200: token sai / đã thu hồi thì phiên vốn đã không còn.
    auth_service.logout(db, refresh_token=request.refresh_token)
    return MessageResponse(message="Đã đăng xuất.")
