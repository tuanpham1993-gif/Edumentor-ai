import os
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

import pytest
from sentence_transformers import SentenceTransformer

from app.services.qdrant_service import (
    generate_course_point_id as q_course_id,
)
from app.services.qdrant_service import (
    generate_skill_point_id as q_skill_id,
)
from app.services.qdrant_service import (
    qdrant_course_service,
    qdrant_skill_service,
)
from scripts.ingest_qdrant import (
    COURSE_COLLECTION_NAME,
    EMBEDDING_MODEL_NAME,
    MAX_SEQ_LENGTH,
    SKILL_COLLECTION_NAME,
    build_course_embedding_text,
    build_skill_embedding_text,
    find_data_dir,
    generate_course_point_id,
    generate_skill_point_id,
    load_all_datasets,
    validate_datasets,
)


def get_model():
    os.environ["HF_HUB_OFFLINE"] = "1"
    return SentenceTransformer(EMBEDDING_MODEL_NAME)


@pytest.fixture(scope="module")
def shared_model():
    return get_model()


def test_find_data_dir():
    data_dir = find_data_dir()
    assert data_dir.is_dir()
    has_course = (data_dir / "course_table.json").is_file() or (data_dir / "courses.json").is_file()
    has_skill = (data_dir / "skill_table.json").is_file() or (data_dir / "skills.json").is_file()
    assert has_course and has_skill


def test_load_all_datasets():
    data_dir = find_data_dir()
    datasets = load_all_datasets(data_dir)
    assert len(datasets["courses"]) == 4509
    assert len(datasets["skills"]) == 5893
    assert len(datasets["course_skills"]) == 14233
    assert len(datasets["skill_relations"]) == 26306


def test_validate_datasets():
    data_dir = find_data_dir()
    datasets = load_all_datasets(data_dir)
    validated = validate_datasets(datasets)
    stats = validated["stats"]

    assert stats["valid_courses"] == 4509
    assert stats["valid_skills"] == 5893
    assert stats["skills_with_courses"] == 5893
    assert stats["skills_without_courses"] == 0
    assert stats["valid_course_skills"] == 14233
    assert stats["valid_skill_relations"] == 26306


def test_deterministic_uuids():
    c_uuid1 = generate_course_point_id(3407)
    c_uuid2 = generate_course_point_id(3407)
    assert c_uuid1 == c_uuid2
    assert c_uuid1 == q_course_id(3407)

    s_uuid1 = generate_skill_point_id(5891)
    s_uuid2 = generate_skill_point_id(5891)
    assert s_uuid1 == s_uuid2
    assert s_uuid1 == q_skill_id(5891)


def test_course_embedding_text_token_limit(shared_model):
    tokenizer = shared_model.tokenizer
    data_dir = find_data_dir()
    datasets = load_all_datasets(data_dir)
    validated = validate_datasets(datasets)

    for cid in list(validated["courses_by_id"].keys())[:50]:
        course = validated["courses_by_id"][cid]
        skills = validated["course_to_skills"].get(cid, [])
        text = build_course_embedding_text(course, skills, tokenizer, MAX_SEQ_LENGTH)

        assert "Course:" in text
        assert "Description:" in text
        assert "Level:" in text
        assert "Organization:" in text
        assert "Related Skills:" in text

        tokens = tokenizer(text, add_special_tokens=True)["input_ids"]
        assert len(tokens) <= MAX_SEQ_LENGTH, f"Course {cid} tokens ({len(tokens)}) exceeded {MAX_SEQ_LENGTH}"


def test_skill_embedding_text_token_limit(shared_model):
    tokenizer = shared_model.tokenizer
    data_dir = find_data_dir()
    datasets = load_all_datasets(data_dir)
    validated = validate_datasets(datasets)

    for sid in list(validated["skills_by_id"].keys())[:50]:
        sname = validated["skills_by_id"][sid]["skill"]
        courses = validated["skill_to_courses"].get(sid, [])
        text = build_skill_embedding_text(sname, courses, tokenizer, MAX_SEQ_LENGTH)

        assert f"Skill: {sname}" in text
        if courses:
            assert "Related Courses:" in text

        tokens = tokenizer(text, add_special_tokens=True)["input_ids"]
        assert len(tokens) <= MAX_SEQ_LENGTH, f"Skill {sid} tokens ({len(tokens)}) exceeded {MAX_SEQ_LENGTH}"


def test_skill_without_courses_embedding(shared_model):
    tokenizer = shared_model.tokenizer
    text = build_skill_embedding_text("Standalone Custom Skill", [], tokenizer, MAX_SEQ_LENGTH)
    assert text == "Skill: Standalone Custom Skill"
    tokens = tokenizer(text, add_special_tokens=True)["input_ids"]
    assert len(tokens) <= MAX_SEQ_LENGTH


def test_all_records_token_budget(shared_model):
    tokenizer = shared_model.tokenizer
    data_dir = find_data_dir()
    datasets = load_all_datasets(data_dir)
    validated = validate_datasets(datasets)

    course_exceeded = 0
    for cid, c in validated["courses_by_id"].items():
        skills = validated["course_to_skills"].get(cid, [])
        text = build_course_embedding_text(c, skills, tokenizer, MAX_SEQ_LENGTH)
        toks = len(tokenizer(text, add_special_tokens=True)["input_ids"])
        if toks > MAX_SEQ_LENGTH:
            course_exceeded += 1

    skill_exceeded = 0
    for sid, s in validated["skills_by_id"].items():
        sname = s.get("skill", "")
        courses = validated["skill_to_courses"].get(sid, [])
        text = build_skill_embedding_text(sname, courses, tokenizer, MAX_SEQ_LENGTH)
        toks = len(tokenizer(text, add_special_tokens=True)["input_ids"])
        if toks > MAX_SEQ_LENGTH:
            skill_exceeded += 1

    assert course_exceeded == 0, f"{course_exceeded} courses exceeded max token length"
    assert skill_exceeded == 0, f"{skill_exceeded} skills exceeded max token length"
    print(f"Verified all {len(validated['courses_by_id'])} courses and {len(validated['skills_by_id'])} skills!")


def test_qdrant_service_definitions():
    assert qdrant_course_service.COLLECTION_NAME == "edumentor_courses"
    assert qdrant_course_service.VECTOR_SIZE == 384
    assert qdrant_skill_service.COLLECTION_NAME == "edumentor_skills"
    assert qdrant_skill_service.VECTOR_SIZE == 384
    assert COURSE_COLLECTION_NAME == "edumentor_courses"
    assert SKILL_COLLECTION_NAME == "edumentor_skills"


if __name__ == "__main__":
    print("Running test_find_data_dir...")
    test_find_data_dir()
    print("Running test_load_all_datasets...")
    test_load_all_datasets()
    print("Running test_validate_datasets...")
    test_validate_datasets()
    print("Running test_deterministic_uuids...")
    test_deterministic_uuids()
    print("Loading shared model...")
    model = get_model()
    print("Running test_course_embedding_text_token_limit...")
    test_course_embedding_text_token_limit(model)
    print("Running test_skill_embedding_text_token_limit...")
    test_skill_embedding_text_token_limit(model)
    print("Running test_skill_without_courses_embedding...")
    test_skill_without_courses_embedding(model)
    print("Running test_all_records_token_budget across all 4509 courses and 5893 skills...")
    test_all_records_token_budget(model)
    print("Running test_qdrant_service_definitions...")
    test_qdrant_service_definitions()
    print("\n>>> ALL TESTS PASSED SUCCESSFULLY! <<<")

