import sys
from pathlib import Path
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi import FastAPI
from fastapi.testclient import TestClient

# Đảm bảo thư mục backend nằm trong sys.path để pytest tìm thấy package 'app'
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.core.database import Base, get_db
from app.routers.v1.api import api_router
from app.core.config import settings

# Tạo FastAPI app riêng cho test để không kích hoạt lifespan kết nối PostgreSQL thật
app = FastAPI()
app.include_router(api_router, prefix=settings.API_STR)

# SQLite in-memory engine cho testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture()
def db_session():
    import app.models  # Đảm bảo nạp đầy đủ metadata của tất cả models
    Base.metadata.create_all(bind=test_engine)
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture()
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()


@pytest.fixture()
def sample_learning_path(db_session):
    from app.models.learning_path import LearningPath, LearningPathNode
    from app.models.skill import Skills

    # Create skills
    python_skill = Skills(skill_id=101, skill="Python", is_active=True)
    fastapi_skill = Skills(skill_id=102, skill="FastAPI", is_active=True)

    # Create a learning path
    learning_path = LearningPath(
        student_id=10,
        original_query="Become a Backend Developer",
        goal_type="career",
        status="ongoing",
    )

    db_session.add_all([python_skill, fastapi_skill, learning_path])
    db_session.flush()

    # Add nodes in the learning path
    python_node = LearningPathNode(
        path_id=learning_path.record_id,
        skill_id=python_skill.skill_id,
        node_role="prerequisite",
        is_target=False,
        added_by="system",
        is_required=True,
        display_order=1000,
    )

    api_node = LearningPathNode(
        path_id=learning_path.record_id,
        skill_id=fastapi_skill.skill_id,
        node_role="prerequisite",
        is_target=False,
        added_by="system",
        is_required=True,
        display_order=2000,
    )

    db_session.add_all([python_node, api_node])
    db_session.commit()

    return {
        "path_id": learning_path.record_id,
        "student_id": learning_path.student_id,
        "python_skill_id": python_skill.skill_id,
        "fastapi_skill_id": fastapi_skill.skill_id,
    }