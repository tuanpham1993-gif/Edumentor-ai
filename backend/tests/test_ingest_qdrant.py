import os
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

import sys
from pathlib import Path
from unittest.mock import MagicMock

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

import pytest
from sentence_transformers import SentenceTransformer

from app.services.qdrant_service import (
    generate_course_point_id as q_course_id,
    generate_skill_point_id as q_skill_id,
    qdrant_course_service,
    qdrant_skill_service,
)
from scripts.ingest_qdrant import (
    COURSE_COLLECTION_NAME,
    EMBEDDING_MODEL_NAME,
    MAX_SEQ_LENGTH,
    SKILL_COLLECTION_NAME,
    TUTOR_SKILL_COLLECTION_NAME,
    backup_collection,
    build_course_embedding_text,
    build_skill_embedding_text,
    clear_collection_points,
    ensure_collection,
    generate_course_point_id,
    generate_skill_point_id,
    load_datasets_from_postgres,
    validate_datasets,
)


def get_model():
    return SentenceTransformer(EMBEDDING_MODEL_NAME)


@pytest.fixture(scope="module")
def shared_model():
    return get_model()


def test_deterministic_uuids():
    c_uuid1 = generate_course_point_id(3407)
    c_uuid2 = generate_course_point_id(3407)
    assert c_uuid1 == c_uuid2
    assert c_uuid1 == q_course_id(3407)

    s_uuid1 = generate_skill_point_id(5891)
    s_uuid2 = generate_skill_point_id(5891)
    assert s_uuid1 == s_uuid2
    assert s_uuid1 == q_skill_id(5891)


def test_postgres_loader_and_validation():
    mock_db = MagicMock()
    mock_c = MagicMock(
        course_id=1,
        title="Test Course",
        num_enrolled=100,
        rating=4.5,
        num_reviews=10,
        instructor="Prof A",
        organization="Org X",
        description="Course description text",
        modules="5 modules",
        level="Beginner",
        schedule="Flexible",
        url="http://test.com",
        image="img.png",
    )
    mock_s = MagicMock(skill_id=10, skill="Python", is_active=True)
    mock_cs = MagicMock(course_id=1, skill_id=10)
    mock_sr = MagicMock(from_skill_id=10, to_skill_id=20, relation_type="prerequisite")

    mock_db.query().all.side_effect = [
        [mock_c],
        [mock_s],
        [mock_cs],
        [mock_sr],
    ]

    datasets = load_datasets_from_postgres(db_session=mock_db)
    assert len(datasets["courses"]) == 1
    assert datasets["courses"][0]["title"] == "Test Course"
    assert len(datasets["skills"]) == 1
    assert datasets["skills"][0]["skill"] == "Python"
    assert len(datasets["course_skill"]) == 1
    assert len(datasets["skill_relation"]) == 1
    assert datasets["source"] == "postgresql"

    validated = validate_datasets(datasets)
    assert len(validated["courses_by_id"]) == 1
    assert len(validated["skills_by_id"]) == 1
    assert validated["course_to_skills"][1] == ["Python"]
    assert len(validated["skill_to_courses"][10]) == 1


def test_course_embedding_text_token_limit(shared_model):
    tokenizer = shared_model.tokenizer
    course = {
        "title": "Machine Learning Specialization",
        "level": "Intermediate",
        "organization": "Stanford",
        "description": "Comprehensive course covering supervised and unsupervised learning.",
    }
    skills = ["Python", "Machine Learning", "Neural Networks"]
    text = build_course_embedding_text(course, skills, tokenizer, MAX_SEQ_LENGTH)

    assert "Course: Machine Learning Specialization" in text
    assert "Description:" in text
    assert "Level:\nIntermediate" in text
    assert "Organization:\nStanford" in text
    assert "Related Skills:\nPython, Machine Learning, Neural Networks" in text

    tokens = tokenizer(text, add_special_tokens=True)["input_ids"]
    assert len(tokens) <= MAX_SEQ_LENGTH


def test_skill_embedding_text_token_limit(shared_model):
    tokenizer = shared_model.tokenizer
    courses = [
        {"course_id": 1, "title": "Python for Everybody", "description": "Learn to program with Python"},
        {"course_id": 2, "title": "Crash Course on Python", "description": "Quick dive into Python"},
    ]
    text = build_skill_embedding_text("Python", courses, tokenizer, MAX_SEQ_LENGTH)

    assert "Skill: Python" in text
    assert "Related Courses:" in text
    assert "1. Python for Everybody" in text
    assert "2. Crash Course on Python" in text

    tokens = tokenizer(text, add_special_tokens=True)["input_ids"]
    assert len(tokens) <= MAX_SEQ_LENGTH


def test_skill_without_courses_embedding(shared_model):
    tokenizer = shared_model.tokenizer
    text = build_skill_embedding_text("Standalone Custom Skill", [], tokenizer, MAX_SEQ_LENGTH)
    assert text == "Skill: Standalone Custom Skill"
    tokens = tokenizer(text, add_special_tokens=True)["input_ids"]
    assert len(tokens) <= MAX_SEQ_LENGTH


def test_qdrant_service_definitions():
    assert qdrant_course_service.COLLECTION_NAME == "edumentor_courses"
    assert qdrant_course_service.VECTOR_SIZE == 384
    assert qdrant_skill_service.COLLECTION_NAME == "edumentor_skills"
    assert qdrant_skill_service.VECTOR_SIZE == 384
    assert COURSE_COLLECTION_NAME == "edumentor_courses"
    assert SKILL_COLLECTION_NAME == "edumentor_skills"
    assert TUTOR_SKILL_COLLECTION_NAME == "tutor_skills"


def test_backup_and_clear_operations():
    mock_client = MagicMock()
    mock_col = MagicMock()
    mock_col.name = "edumentor_courses"
    mock_client.get_collections.return_value.collections = [mock_col]
    mock_snap = MagicMock(name="snapshot-1.snapshot")
    mock_client.create_snapshot.return_value = mock_snap

    # 1. Test backup_collection
    snap = backup_collection(mock_client, "edumentor_courses")
    assert snap is not None
    mock_client.create_snapshot.assert_called_with(collection_name="edumentor_courses", wait=True)

    # 2. Test clear_collection_points
    clear_collection_points(mock_client, "edumentor_courses")
    mock_client.delete.assert_called()


if __name__ == "__main__":
    print("Running test_deterministic_uuids...")
    test_deterministic_uuids()
    print("Running test_postgres_loader_and_validation...")
    test_postgres_loader_and_validation()
    print("Loading shared model...")
    model = get_model()
    print("Running test_course_embedding_text_token_limit...")
    test_course_embedding_text_token_limit(model)
    print("Running test_skill_embedding_text_token_limit...")
    test_skill_embedding_text_token_limit(model)
    print("Running test_skill_without_courses_embedding...")
    test_skill_without_courses_embedding(model)
    print("Running test_qdrant_service_definitions...")
    test_qdrant_service_definitions()
    print("Running test_backup_and_clear_operations...")
    test_backup_and_clear_operations()
    print("\n>>> ALL INGESTION TESTS PASSED SUCCESSFULLY! <<<")
