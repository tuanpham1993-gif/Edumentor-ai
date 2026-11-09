#shared test configuration and fixtures.import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from app.core.database import Base, get_db
import pytest

from fastapi import FastAPI
from app.routers.v1.api import api_router
from app.core.config import settings

app = FastAPI()
app.include_router(api_router, prefix=settings.API_STR)

SQLALCHEMY_DATABASE_URL = "sqlite://"
test_engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)
#check_same_thread: allows the connection to be used across different threads. This matters because TestClient may execute requests in a different thread
#StaticPool: reuses the same connection so the in-memory database remains available across sessions.
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture()
def db_session():
    import app.models
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
        yield db_session
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

    # Create skills.
    python_skill = Skills(skill_id=101, skill="Python",is_active=True,)
    fastapi_skill = Skills(skill_id=102,skill="FastAPI",is_active=True,)

    # Create a learning path.
    learning_path = LearningPath(student_id=10, original_query="Become a Backend Developer", goal_type="career", status="ongoing")

    db_session.add_all([python_skill, fastapi_skill, learning_path,])
    db_session.flush()

    # Add Python as a node in the learning path.
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


# ─────────────── Token đăng nhập dùng chung (module 01 · Tuấn · 09/11/2026) ───────────────
# Dùng cho mọi test cần gọi API có require_admin / get_current_user:
#     def test_xxx(client, admin_headers):
#         client.post("/api/skills", json={...}, headers=admin_headers)
# Đăng nhập thật qua POST /api/auth/login (không tự ký JWT) → test đúng như người dùng thật.

ADMIN_EMAIL = "admin.test@edumentor.vn"
STUDENT_EMAIL = "student.test@edumentor.vn"
TEST_PASSWORD = "Test@1234"


def _login_headers(client, email, password=TEST_PASSWORD):
    response = client.post("/api/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.fixture()
def admin_headers(client, db_session):
    """Header Bearer của một tài khoản admin (tạo bằng scripts.create_admin)."""
    from scripts.create_admin import create_admin

    create_admin(db_session, email=ADMIN_EMAIL, full_name="Admin Test", password=TEST_PASSWORD)
    return _login_headers(client, ADMIN_EMAIL)


@pytest.fixture()
def student_headers(client):
    """Header Bearer của một học viên thường (đăng ký qua API) — dùng để kiểm tra bị chặn 403."""
    response = client.post(
        "/api/auth/register",
        json={
            "full_name": "Student Test",
            "email": STUDENT_EMAIL,
            "password": TEST_PASSWORD,
            "confirm_password": TEST_PASSWORD,
        },
    )
    assert response.status_code == 201, response.text
    return _login_headers(client, STUDENT_EMAIL)