# backend/app/repositories/user_repository.py
from sqlalchemy import select
from sqlalchemy.orm import Session
 
from app.models.user import Users
 
 
def get_by_email(db: Session, email: str) -> Users | None:
    return db.scalar(select(Users).where(Users.email == email))
 
 
def get_by_id(db: Session, user_id: int) -> Users | None:
    return db.get(Users, user_id)
 
 
def create(db: Session, *, email: str, full_name: str, hashed_password: str) -> Users:
    user = Users(email=email, full_name=full_name, hashed_password=hashed_password)
    db.add(user)
    db.flush()  # gửi INSERT để có user_id, nhưng chưa commit
    return user
 