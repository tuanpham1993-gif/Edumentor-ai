from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings
from app.services.qdrant_service import qdrant_skill_service
from app.core.embedding_model import generate_embedding_skills_name

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
    from app.core.seed_data.seed_data_code import seed_data
    create_tables()
    seed_data(SessionLocal())
    if(qdrant_skill_service.create_collection()):
        query = text("""
        SELECT skill_id, skill
        FROM skills WHERE is_active = TRUE
        ORDER BY skill_id""")
        with engine.connect() as conn:
            rows_skill = conn.execute(query).mappings().all()
        skills = [
            {
                "skill_id": row["skill_id"],
                "skill_name": row["skill"]
            }
            for row in rows_skill
        ]

        skill_names = [
            skill["skill_name"]
            for skill in skills
        ]
        embedding = generate_embedding_skills_name(skill_names)
        qdrant_skill_service.index_skill(skills, embedding)

        

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()