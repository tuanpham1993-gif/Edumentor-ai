# backend/app/routers/v1/endpoints/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
 
from app.core.database import get_db
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.schemas.user import UserMe
from app.services import auth_service
 
router = APIRouter()
 
 
@router.post(
    "/register",
    response_model=UserMe,
    status_code=status.HTTP_201_CREATED,
    summary="Đăng ký tài khoản",
)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    try:
        return auth_service.register(
            db,
            email=request.email,
            full_name=request.full_name,
            password=request.password,  # không truyền confirm_password xuống
        )
    except auth_service.EmailAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email đã được sử dụng.",
        ) from None
 
 
@router.post("/login", response_model=TokenResponse, summary="Đăng nhập")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    result = auth_service.login(db, email=request.email, password=request.password)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email hoặc mật khẩu không đúng.",
        )
    token, user = result
    return TokenResponse(access_token=token, user=user)
 