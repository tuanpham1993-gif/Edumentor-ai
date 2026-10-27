from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.SQL_ECHO,   # True -> in ra màn hình câu lệnh SQL mà ORM sinh ra
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def create_tables() -> None:
    import app.models
    Base.metadata.create_all(bind=engine)

def init_db() -> None:
    """Gọi một lần lúc ứng dụng khởi động."""
    create_tables()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()