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
    """Tuấn 22/11 (G2a): tạo / nâng cấp bảng bằng Alembic (app/core/migrations.py). Alembic lỗi (vd đang ở nhánh
    cũ chưa có file migration mới → "Can't locate revision") → ghi cảnh báo, rơi về create_all như trước, server vẫn chạy.
    """
    import app.models  # noqa: F401 — đăng ký mọi bảng

    try:
        from app.core.migrations import current_revision, run_migrations

        action = run_migrations(engine)
        print(f"[INFO] Database: {action} → Alembic {current_revision(engine)}")
    except Exception as e:  # noqa: BLE001
        print(f"[WARNING] Alembic migration lỗi, chỉ chạy create_all: {e}")
        Base.metadata.create_all(bind=engine)
    sync_notification_types()


def sync_notification_types(bind=None) -> bool:
    """Tuấn 21/11: bảng `notifications` đã tạo ở mọi máy với CHECK chỉ cho các loại cũ; create_all không sửa bảng
    có sẵn và dự án chưa có Alembic (G2a). Khi TYPES có loại mới (vd "review_due") → tạo lại CHECK cho khớp.
    Chạy lại nhiều lần vẫn an toàn (đã khớp thì không làm gì). Chỉ PostgreSQL; SQLite (test) tạo bảng mới từ model.
    Trả True nếu đã sửa."""
    from app.models.notification import TYPES

    bind = bind or engine
    if bind.dialect.name != "postgresql":
        return False
    with bind.begin() as conn:
        definition = conn.execute(
            text(
                "SELECT pg_get_constraintdef(c.oid) FROM pg_constraint c JOIN pg_class t ON t.oid = c.conrelid "
                "WHERE t.relname = 'notifications' AND c.conname = 'ck_notifications_type'"
            )
        ).scalar()
        if definition is not None and all(f"'{t}'" in definition for t in TYPES):
            return False
        allowed = ", ".join(f"'{t}'" for t in TYPES)  # TYPES là hằng trong code, không phải dữ liệu người dùng
        conn.execute(text("ALTER TABLE notifications DROP CONSTRAINT IF EXISTS ck_notifications_type"))
        conn.execute(
            text(f"ALTER TABLE notifications ADD CONSTRAINT ck_notifications_type CHECK (type IN ({allowed}))")
        )
    return True


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
    # Tuấn 21/11: database mới (vd Docker lần đầu) → tự nạp đề ôn tập + embedding, thay 4 lệnh tay. Chỉ khi bảng
    # review_questions trống; lỗi chỉ ghi log. Chạy SAU seed_data() vì cần khóa học + kỹ năng.
    try:
        from app.core.seed_data import review_autoseed

        review_autoseed.run(SessionLocal)
    except Exception as e:
        print(f"[WARNING] Review bank auto-seed failed: {e}")
    index_skills_to_qdrant()


def index_skills_to_qdrant() -> None:
    """Hòa: đánh chỉ mục tên kỹ năng vào Qdrant (lần đầu tạo collection) để gợi ý lộ trình tìm kỹ năng gần nghĩa.
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


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
