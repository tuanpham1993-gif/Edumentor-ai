from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
 
from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import Users
 
# Đọc header "Authorization: Bearer <token>".
# auto_error=False: thiếu header thì trả None, để mình tự quyết định trả 401.
bearer_scheme = HTTPBearer(auto_error=False)
 
 
def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> Users:
    """Trả về user đang đăng nhập; không hợp lệ → 401."""
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Phiên đăng nhập không hợp lệ hoặc đã hết hạn.",
        headers={"WWW-Authenticate": "Bearer"},
    )
 
    if credentials is None:
        raise unauthorized
 
    user_id = decode_access_token(credentials.credentials)
    if user_id is None:
        raise unauthorized
 
    user = db.get(Users, user_id)
    if user is None or not user.is_active:
        raise unauthorized
 
    return user
 
 
def require_admin(current_user: Users = Depends(get_current_user)) -> Users:
    """Chỉ cho admin đi tiếp; người khác → 403."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền thực hiện thao tác này.",
        )
    return current_user