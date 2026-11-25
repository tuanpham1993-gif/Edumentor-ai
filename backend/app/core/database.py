from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.SQL_ECHO,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


def create_tables() -> None:
    import app.models

    Base.metadata.create_all(bind=engine)


def init_db() -> None:
    """Gọi một lần lúc ứng dụng khởi động."""
    create_tables()
    try:
        from app.core.seed_data.seed_data_code import seed_data
        seed_data(SessionLocal())
    except FileNotFoundError as e:
        print(f"[WARNING] Seed data file not found, skipping seed: {e}")
    except Exception as e:
        print(f"[WARNING] Seed data failed: {e}")
    try:
        # learning_path2 form options: certifications, technical domains
        from app.core.seed_data.seed_profile_reference import seed_profile_reference
        seed_profile_reference(SessionLocal())
    except Exception as e:  # noqa: BLE001
        print(f"[WARNING] Seed profile reference failed: {e}")
    index_skills_to_qdrant()

def index_skills_to_qdrant() -> None:
    """ đánh chỉ mục tên kỹ năng vào Qdrant (lần đầu tạo collection) để gợi ý lộ trình tìm kỹ năng gần nghĩa.
    Import mô hình + Qdrant NGAY TRONG HÀM (không ở đầu file) và bọc try: máy không chạy Qdrant / chưa cài
    sentence-transformers thì server vẫn khởi động, chỉ in cảnh báo (gộp nhánh 13/11)."""
    try:
        import httpx

        # Hỏi Qdrant trước (2 giây): không chạy thì bỏ qua NGAY — QdrantClient tự thử lại tới ~100 giây,
        # làm server khởi động chậm gần 2 phút trên máy không chạy Qdrant (đo 13/11).
        httpx.get(f"{settings.QDRANT_URL}/readyz", timeout=2.0).raise_for_status()
        from app.core.embedding_model import generate_embedding_skills_name
        from app.services.qdrant_service import qdrant_skill_service

        if qdrant_skill_service.create_collection():
            query = text("SELECT skill_id, skill FROM skills WHERE is_active = TRUE ORDER BY skill_id")
            with engine.connect() as conn:
                rows_skill = conn.execute(query).mappings().all()
            skills = [{"skill_id": row["skill_id"], "skill_name": row["skill"]} for row in rows_skill]
            embedding = generate_embedding_skills_name([skill["skill_name"] for skill in skills])
            qdrant_skill_service.index_skill(skills, embedding)
    except Exception as e:  # noqa: BLE001 — tính năng phụ, không được làm sập server
        print(f"[WARNING] Bỏ qua đánh chỉ mục kỹ năng vào Qdrant: {e}")
        return
    try:
        # AI learning path: skill aliases, job roles, role aliases, role candidate skills -> Qdrant
        from app.core.seed_data.seed_ai_data import seed_ai_data
        seed_ai_data(SessionLocal())
    except FileNotFoundError as e:
        print(f"[WARNING] AI reference data file not found, skipping: {e}")
    except Exception as e:  # noqa: BLE001
        print(f"[WARNING] Bỏ qua nạp dữ liệu AI (alias, vai trò) vào Qdrant: {e}")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
