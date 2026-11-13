import httpx
from fastapi import Request

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import Users
"""Dependency dùng chung: biết "ai đang gọi API" (module 01 · Tuấn · GĐ1, 05/11/2026).

`Depends(x)` của FastAPI nghĩa là: trước khi chạy API, hãy chạy hàm x và đưa kết quả vào.
Gom 4 bước (lấy token → giải mã → tìm user trong DB → trả user) vào MỘT hàm,
mọi API cần đăng nhập chỉ việc khai báo `current_user: Users = Depends(get_current_user)`.

    401 Unauthorized = "không biết bạn là ai" (thiếu/sai/hết hạn token, user không còn)
    403 Forbidden    = "biết bạn là ai nhưng bạn không có quyền" (student gọi API admin)
"""
# Đọc header "Authorization: Bearer <token>". Nhờ nó Swagger có nút "Authorize".
# auto_error=False: thiếu header thì trả None, để mình tự quyết định trả 401.
bearer_scheme = HTTPBearer(auto_error=False)
def get_llm_client(request: Request) -> httpx.AsyncClient:
    return request.app.state.llm_client

def get_llm_client_base(request: Request) -> httpx.AsyncClient:
    return request.app.state.llm_client_base

def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> Users:
    """Trả về user đang đăng nhập; không hợp lệ → 401."""
    # Mọi trường hợp thất bại dùng CHUNG một thông báo → không lộ lý do cụ thể
    # (vd "user không tồn tại" vs "token sai") cho kẻ dò.
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Phiên đăng nhập không hợp lệ hoặc đã hết hạn.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Bước 1: có gửi header Authorization không?
    if credentials is None:
        raise unauthorized

    # Bước 2: giải mã token (credentials.credentials là phần "eyJ..." sau chữ Bearer)
    user_id = decode_access_token(credentials.credentials)
    if user_id is None:
        raise unauthorized

    # Bước 3: tìm user trong DB. Vai trò lấy từ DB chứ không tin token → hạ quyền có hiệu lực ngay.
    # Kiểm `is None` TRƯỚC `is_active`, nếu không `None.is_active` sẽ lỗi.
    user = db.get(Users, user_id)
    if user is None or not user.is_active:
        raise unauthorized

    # Bước 4: đưa user cho API dùng.
    # Trong một request FastAPI chỉ gọi get_db() một lần → `user` và `db` của API là cùng phiên,
    # nên API sửa user rồi db.commit() là lưu được (dùng ở PATCH /me, change-password).
    return user


def require_admin(current_user: Users = Depends(get_current_user)) -> Users:
    """Chỉ cho admin đi tiếp; người khác → 403.

    Depends lồng nhau: require_admin → get_current_user → (bearer_scheme, get_db).
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền thực hiện thao tác này.",
        )
    return current_user
