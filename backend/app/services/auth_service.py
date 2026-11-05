# backend/app/services/auth_service.py
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
 
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import Users
from app.repositories import user_repository
 
 
class EmailAlreadyExistsError(Exception):
    """Email đã được dùng để đăng ký."""
 
 
def register(db: Session, *, email: str, full_name: str, password: str) -> Users:
    """Tạo tài khoản student mới (FR-01). Email trùng → EmailAlreadyExistsError."""
    if user_repository.get_by_email(db, email) is not None:
        raise EmailAlreadyExistsError
 
    try:
        user = user_repository.create(
            db,
            email=email,
            full_name=full_name,
            hashed_password=hash_password(password),
        )
        db.commit()
    except IntegrityError:
        db.rollback()
        raise EmailAlreadyExistsError from None
 
    db.refresh(user)  # đọc lại các giá trị DB tự điền: role, created_at...
    return user
 
 
def login(db: Session, *, email: str, password: str) -> tuple[str, Users] | None:
    """Đúng email + mật khẩu và tài khoản còn hoạt động → (token, user). Ngược lại → None."""
    user = user_repository.get_by_email(db, email)
    if user is None:
        return None
 
    if not verify_password(password, user.hashed_password):
        return None
 
    if not user.is_active:
        return None
 
    token = create_access_token(user.user_id)
    return token, user
 