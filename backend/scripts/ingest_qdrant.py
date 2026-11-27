"""
EduMentor AI - Data Ingestion Service
Directly ingests embeddings from PostgreSQL database tables into Qdrant collections:
- `courses` table (Model: Courses) -> `edumentor_courses`
- `skills` table (Model: Skills) -> `edumentor_skills` & `tutor_skills`
- `course_skill` table (Model: CourseSkill)
- `skill_relation` table (Model: SkillRelation)

Embedding Model:
- sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 (dim=384, Cosine)
"""

import argparse
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any
from uuid import NAMESPACE_URL, uuid5

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, Filter, PointStruct, VectorParams
from sentence_transformers import SentenceTransformer

# Add backend directory to sys.path
_current_file_dir = Path(__file__).resolve().parent
_backend_dir = _current_file_dir.parent
if str(_backend_dir) not in sys.path:
    sys.path.insert(0, str(_backend_dir))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("ingest_qdrant")

# ==========================================
# CONFIGURATION CONSTANTS
# ==========================================
EMBEDDING_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
EMBEDDING_DIMENSION = 384
MAX_SEQ_LENGTH = 128
DEFAULT_BATCH_SIZE = 128

COURSE_COLLECTION_NAME = "edumentor_courses"
SKILL_COLLECTION_NAME = "edumentor_skills"
TUTOR_SKILL_COLLECTION_NAME = "tutor_skills"

TABLE_COURSES = "courses"
TABLE_SKILLS = "skills"
TABLE_COURSE_SKILL = "course_skill"
TABLE_SKILL_RELATION = "skill_relation"


# ==========================================
# STABLE POINT ID GENERATORS (UUID5)
# ==========================================
def generate_course_point_id(course_id: int) -> str:
    """Generate deterministic UUID for course point based on course_id."""
    return str(uuid5(NAMESPACE_URL, f"edumentor-course:{course_id}"))


def generate_skill_point_id(skill_id: int) -> str:
    """Generate deterministic UUID for skill point based on skill_id."""
    return str(uuid5(NAMESPACE_URL, f"edumentor-skill:{skill_id}"))


# ==========================================
# POSTGRESQL DATA LOADING (EXCLUSIVE SOURCE)
# ==========================================
def load_datasets_from_postgres(db_session=None) -> dict[str, Any]:
    """
    Loads all datasets directly from PostgreSQL database tables:
    - courses
    - skills
    - course_skill
    - skill_relation
    """
    from app.core.database import SessionLocal
    from app.models.course import Courses
    from app.models.skill import Skills
    from app.models.course_skill import CourseSkill
    from app.models.skill_relation import SkillRelation

    close_session = False
    if db_session is None:
        db_session = SessionLocal()
        close_session = True

    try:
        logger.info(f"Reading from PostgreSQL table '{TABLE_COURSES}'...")
        c_records = db_session.query(Courses).all()
        courses_raw = [
            {
                "course_id": c.course_id,
                "title": c.title,
                "num_enrolled": c.num_enrolled,
                "rating": c.rating,
                "num_reviews": c.num_reviews,
                "instructor": c.instructor,
                "organization": c.organization,
                "description": c.description,
                "modules": c.modules,
                "level": c.level,
                "schedule": c.schedule,
                "url": c.url,
                "image": c.image,
            }
            for c in c_records
        ]

        logger.info(f"Reading from PostgreSQL table '{TABLE_SKILLS}'...")
        s_records = db_session.query(Skills).all()
        skills_raw = [
            {
                "skill_id": s.skill_id,
                "skill": s.skill,
                "is_active": s.is_active,
            }
            for s in s_records
        ]

        logger.info(f"Reading from PostgreSQL table '{TABLE_COURSE_SKILL}'...")
        cs_records = db_session.query(CourseSkill).all()
        cs_raw = [
            {"course_id": cs.course_id, "skill_id": cs.skill_id}
            for cs in cs_records
        ]

        logger.info(f"Reading from PostgreSQL table '{TABLE_SKILL_RELATION}'...")
        sr_records = db_session.query(SkillRelation).all()
        sr_raw = [
            {
                "from_skill_id": sr.from_skill_id,
                "to_skill_id": sr.to_skill_id,
                "relation_type": sr.relation_type,
            }
            for sr in sr_records
        ]

        return {
            "courses": courses_raw,
            "skills": skills_raw,
            "course_skill": cs_raw,
            "skill_relation": sr_raw,
            # Convenient aliases
            "course_skills": cs_raw,
            "skill_relations": sr_raw,
            "source": "postgresql",
        }
    finally:
        if close_session:
            db_session.close()


# ==========================================
# VALIDATION & INTEGRITY CHECKING
# ==========================================
def validate_datasets(datasets: dict[str, Any]) -> dict[str, Any]:
    """
    Validates integrity of database records and constructs relational mappings:
    - course_to_skills
    - skill_to_courses
    - skill_relations_map
    """
    courses_raw = datasets.get("courses") or []
    skills_raw = datasets.get("skills") or []
    cs_raw = datasets.get("course_skill") or datasets.get("course_skills") or []
    sr_raw = datasets.get("skill_relation") or datasets.get("skill_relations") or []

    if not courses_raw:
        raise ValueError(f"Table '{TABLE_COURSES}' has no records.")
    if not skills_raw:
        raise ValueError(f"Table '{TABLE_SKILLS}' has no records.")

    # 1. Index Courses by ID
    courses_by_id: dict[int, dict[str, Any]] = {}
    for c in courses_raw:
        cid = c.get("course_id")
        if cid is not None and c.get("title"):
            courses_by_id[int(cid)] = c

    # 2. Index Skills by ID
    skills_by_id: dict[int, dict[str, Any]] = {}
    for s in skills_raw:
        sid = s.get("skill_id")
        if sid is not None and s.get("skill"):
            skills_by_id[int(sid)] = s

    # 3. Build Course <-> Skill Mappings
    course_to_skills: dict[int, list[str]] = {}
    skill_to_courses: dict[int, list[dict[str, Any]]] = {}
    for cs in cs_raw:
        cid = cs.get("course_id")
        sid = cs.get("skill_id")
        if cid is None or sid is None:
            continue
        try:
            cid, sid = int(cid), int(sid)
        except (ValueError, TypeError):
            continue

        if cid in courses_by_id and sid in skills_by_id:
            sname = skills_by_id[sid].get("skill")
            if sname:
                course_to_skills.setdefault(cid, []).append(sname)
            skill_to_courses.setdefault(sid, []).append(courses_by_id[cid])

    # 4. Build Skill Relationships Map
    skill_relations_map: dict[int, dict[str, list[str]]] = {}
    for sr in sr_raw:
        fid = sr.get("from_skill_id")
        tid = sr.get("to_skill_id")
        rtype = str(sr.get("relation_type") or "related").strip().lower()
        if fid is None or tid is None:
            continue
        try:
            fid, tid = int(fid), int(tid)
        except (ValueError, TypeError):
            continue

        if fid in skills_by_id and tid in skills_by_id:
            tname = skills_by_id[tid].get("skill")
            if tname:
                skill_relations_map.setdefault(fid, {"prerequisites": [], "related": []})
                if rtype == "prerequisite":
                    skill_relations_map[fid]["prerequisites"].append(tname)
                else:
                    skill_relations_map[fid]["related"].append(tname)

    return {
        "courses_by_id": courses_by_id,
        "skills_by_id": skills_by_id,
        "course_to_skills": course_to_skills,
        "skill_to_courses": skill_to_courses,
        "skill_relations_map": skill_relations_map,
        "stats": {
            "valid_courses": len(courses_by_id),
            "valid_skills": len(skills_by_id),
            "valid_course_skill": len(cs_raw),
            "valid_skill_relation": len(sr_raw),
            "skills_with_courses": len(skill_to_courses),
            "skills_without_courses": len(skills_by_id) - len(skill_to_courses),
        },
    }


# ==========================================
# EMBEDDING TEXT BUILDERS (TOKEN-BUDGET CONTROLLED)
# ==========================================
def build_course_embedding_text(
    course: dict[str, Any],
    related_skills: list[str],
    tokenizer: Any,
    max_tokens: int = MAX_SEQ_LENGTH,
) -> str:
    """Builds Course embedding text conforming to the token limit."""
    title = str(course.get("title") or "").strip()
    level = str(course.get("level") or "N/A").strip()
    org = str(course.get("organization") or "N/A").strip()
    desc = str(course.get("description") or "").strip()

    unique_skills = list(dict.fromkeys(related_skills))
    skills_str = ", ".join(unique_skills) if unique_skills else "N/A"

    prefix = f"Course: {title}\n\nDescription:\n"
    suffix = f"\n\nLevel:\n{level}\n\nOrganization:\n{org}\n\nRelated Skills:\n{skills_str}"

    prefix_tokens = tokenizer(prefix, add_special_tokens=False, truncation=False)["input_ids"]
    suffix_tokens = tokenizer(suffix, add_special_tokens=False, truncation=False)["input_ids"]
    fixed_count = len(prefix_tokens) + len(suffix_tokens) + 2

    if fixed_count >= max_tokens:
        trimmed_skills = list(unique_skills)
        while trimmed_skills and fixed_count >= max_tokens:
            trimmed_skills.pop()
            skills_str = ", ".join(trimmed_skills) if trimmed_skills else "N/A"
            suffix = f"\n\nLevel:\n{level}\n\nOrganization:\n{org}\n\nRelated Skills:\n{skills_str}"
            suffix_tokens = tokenizer(suffix, add_special_tokens=False, truncation=False)["input_ids"]
            fixed_count = len(prefix_tokens) + len(suffix_tokens) + 2
        desc_budget = max(0, max_tokens - fixed_count)
    else:
        desc_budget = max_tokens - fixed_count

    if desc and desc_budget > 0:
        desc_tokens = tokenizer(desc, add_special_tokens=False, truncation=False)["input_ids"]
        if len(desc_tokens) > desc_budget:
            truncated_desc = tokenizer.decode(desc_tokens[:desc_budget], skip_special_tokens=True).strip()
        else:
            truncated_desc = desc
    else:
        truncated_desc = ""

    return f"{prefix}{truncated_desc}{suffix}".strip()


def build_skill_embedding_text(
    skill_name: str,
    related_courses: list[dict[str, Any]],
    tokenizer: Any,
    max_tokens: int = MAX_SEQ_LENGTH,
) -> str:
    """Builds Skill embedding text conforming to the token limit."""
    skill_name = str(skill_name or "").strip()
    if not related_courses:
        return f"Skill: {skill_name}"

    header = f"Skill: {skill_name}\n\nRelated Courses:\n\n"
    header_tokens = tokenizer(header, add_special_tokens=False, truncation=False)["input_ids"]
    budget = max_tokens - len(header_tokens) - 2

    if budget <= 0:
        return f"Skill: {skill_name}"

    body_parts = []
    seen_cids = set()
    for idx, c in enumerate(related_courses, start=1):
        cid = c.get("course_id")
        if cid in seen_cids:
            continue
        seen_cids.add(cid)

        ctitle = str(c.get("title") or "").strip()
        cdesc = str(c.get("description") or "").strip()
        c_prefix = f"{idx}. {ctitle}\n\nDescription:\n"
        c_prefix_tokens = tokenizer(c_prefix, add_special_tokens=False, truncation=False)["input_ids"]

        if len(c_prefix_tokens) >= budget:
            break

        desc_budget = budget - len(c_prefix_tokens)
        cdesc_tokens = tokenizer(cdesc, add_special_tokens=False, truncation=False)["input_ids"]

        if len(cdesc_tokens) > desc_budget:
            trunc_cdesc = tokenizer.decode(cdesc_tokens[:desc_budget], skip_special_tokens=True).strip()
            body_parts.append(f"{c_prefix}{trunc_cdesc}\n\n")
            break
        else:
            body_parts.append(f"{c_prefix}{cdesc}\n\n")
            budget -= (len(c_prefix_tokens) + len(cdesc_tokens))
            if budget <= 10:
                break

    body = "".join(body_parts).strip()
    return f"{header}{body}".strip() if body else f"Skill: {skill_name}"


# ==========================================
# QDRANT OPERATIONS
# ==========================================
def wait_for_qdrant(qdrant_url: str, timeout_seconds: int = 60) -> QdrantClient:
    """Connects to Qdrant and verifies health."""
    client = QdrantClient(url=qdrant_url)
    start_time = time.time()
    last_err = None

    logger.info(f"Connecting to Qdrant at: {qdrant_url}...")
    while time.time() - start_time < timeout_seconds:
        try:
            client.get_collections()
            logger.info("Successfully connected to Qdrant.")
            return client
        except Exception as e:  # noqa: BLE001
            last_err = e
            time.sleep(2)

    raise ConnectionError(f"Failed to connect to Qdrant at {qdrant_url}: {last_err}")


def backup_collection(client: QdrantClient, collection_name: str) -> str | None:
    """Creates a snapshot backup of the collection if it exists."""
    try:
        collections = {c.name for c in client.get_collections().collections}
        if collection_name in collections:
            snapshot = client.create_snapshot(collection_name=collection_name, wait=True)
            snapshot_name = getattr(snapshot, "name", str(snapshot))
            logger.info(f"Backup snapshot created for '{collection_name}': {snapshot_name}")
            return str(snapshot_name)
    except Exception as e:
        logger.warning(f"Could not create backup snapshot for '{collection_name}': {e}")
    return None


def ensure_collection(client: QdrantClient, collection_name: str, vector_size: int = EMBEDDING_DIMENSION) -> None:
    """Ensures collection exists with Cosine distance and correct vector size."""
    collections = {c.name for c in client.get_collections().collections}
    if collection_name in collections:
        return

    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
    )
    logger.info(f"Created collection '{collection_name}' (dim={vector_size}, distance=COSINE).")


def clear_collection_points(client: QdrantClient, collection_name: str) -> None:
    """Deletes all existing points from collection while preserving configuration."""
    logger.info(f"Clearing points in collection '{collection_name}'...")
    client.delete(collection_name=collection_name, points_selector=Filter(), wait=True)


def upsert_points_in_batches(
    client: QdrantClient,
    collection_name: str,
    points: list[PointStruct],
    batch_size: int = DEFAULT_BATCH_SIZE,
) -> int:
    """Upserts points into Qdrant in batches."""
    for start in range(0, len(points), batch_size):
        batch = points[start : start + batch_size]
        client.upsert(collection_name=collection_name, points=batch, wait=True)
    return len(points)


# ==========================================
# MAIN INGESTION PIPELINE (PURE POSTGRESQL)
# ==========================================
def run_ingestion(
    qdrant_url: str | None = None,
    batch_size: int = DEFAULT_BATCH_SIZE,
    test_search: bool = False,
    sync_tutor_skills: bool = True,
    clear_points: bool = True,
) -> int:
    """
    Executes PostgreSQL -> Qdrant ingestion:
    1. Read datasets directly from PostgreSQL tables.
    2. Validate records and build relationships.
    3. Ensure Qdrant collections exist and clear old points.
    4. Encode embeddings and upsert deterministic points.
    5. Verify counts and test search.
    """
    qdrant_url = qdrant_url or os.environ.get("QDRANT_URL", "http://localhost:6335")

    print("\n=======================================================")
    print("   EDUMENTOR AI - POSTGRESQL TO QDRANT INGESTION       ")
    print("=======================================================\n")

    # 1. Read PostgreSQL
    print("[1] Loading datasets from PostgreSQL tables...")
    datasets = load_datasets_from_postgres()
    print(f"    - Table '{TABLE_COURSES}':       {len(datasets['courses'])} rows")
    print(f"    - Table '{TABLE_SKILLS}':        {len(datasets['skills'])} rows")
    print(f"    - Table '{TABLE_COURSE_SKILL}':  {len(datasets['course_skill'])} rows")
    print(f"    - Table '{TABLE_SKILL_RELATION}': {len(datasets['skill_relation'])} rows")

    # 2. Validate
    print("\n[2] Validating records and building relationships...")
    validated = validate_datasets(datasets)
    courses_by_id = validated["courses_by_id"]
    skills_by_id = validated["skills_by_id"]
    print(f"    - Valid courses: {len(courses_by_id)}")
    print(f"    - Valid skills:  {len(skills_by_id)}")

    # 3. Connect to Qdrant & Prepare Collections
    print("\n[3] Connecting to Qdrant...")
    qdrant_client = wait_for_qdrant(qdrant_url)
    target_collections = [COURSE_COLLECTION_NAME, SKILL_COLLECTION_NAME]
    if sync_tutor_skills:
        target_collections.append(TUTOR_SKILL_COLLECTION_NAME)

    for col in target_collections:
        backup_collection(qdrant_client, col)
        ensure_collection(qdrant_client, col, vector_size=EMBEDDING_DIMENSION)
        if clear_points:
            clear_collection_points(qdrant_client, col)

    # 4. Load Embedding Model
    print(f"\n[4] Loading embedding model: {EMBEDDING_MODEL_NAME}...")
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    tokenizer = model.tokenizer

    # 5. Ingest Courses
    print(f"\n[5] Encoding and upserting Courses into '{COURSE_COLLECTION_NAME}'...")
    course_items, course_texts = [], []
    for cid, c in courses_by_id.items():
        skills = validated["course_to_skills"].get(cid, [])
        text = build_course_embedding_text(c, skills, tokenizer, max_tokens=MAX_SEQ_LENGTH)
        payload = {
            "course_id": cid,
            "title": str(c.get("title") or ""),
            "level": str(c.get("level") or "N/A"),
            "organization": str(c.get("organization") or "N/A"),
            "instructor": str(c.get("instructor") or "N/A"),
            "rating": float(c.get("rating")) if c.get("rating") is not None else None,
            "num_reviews": int(c.get("num_reviews")) if c.get("num_reviews") is not None else None,
            "description": str(c.get("description") or ""),
            "modules": str(c.get("modules") or ""),
            "schedule": str(c.get("schedule") or ""),
            "url": str(c.get("url") or ""),
            "skills": skills,
            "num_skills": len(skills),
        }
        course_items.append((cid, payload))
        course_texts.append(text)

    course_embeddings = model.encode(course_texts, batch_size=batch_size, normalize_embeddings=True, show_progress_bar=False)
    course_points = [
        PointStruct(id=generate_course_point_id(cid), vector=emb.tolist(), payload=payload)
        for (cid, payload), emb in zip(course_items, course_embeddings)
    ]
    upserted_courses = upsert_points_in_batches(qdrant_client, COURSE_COLLECTION_NAME, course_points, batch_size=batch_size)
    print(f"    Upserted {upserted_courses} points to '{COURSE_COLLECTION_NAME}'.")

    # 6. Ingest Skills
    print(f"\n[6] Encoding and upserting Skills into '{SKILL_COLLECTION_NAME}'...")
    skill_items, skill_texts = [], []
    for sid, s in skills_by_id.items():
        sname = str(s.get("skill") or "")
        related_courses = validated["skill_to_courses"].get(sid, [])
        text = build_skill_embedding_text(sname, related_courses, tokenizer, max_tokens=MAX_SEQ_LENGTH)
        rel_info = validated["skill_relations_map"].get(sid, {})
        payload = {
            "skill_id": sid,
            "skill": sname,
            "is_active": s.get("is_active", True),
            "num_courses": len(related_courses),
            "prerequisites": rel_info.get("prerequisites", []),
            "related_skills": rel_info.get("related", []),
            "top_courses": [c.get("title") for c in related_courses[:5]],
        }
        skill_items.append((sid, payload))
        skill_texts.append(text)

    skill_embeddings = model.encode(skill_texts, batch_size=batch_size, normalize_embeddings=True, show_progress_bar=False)
    skill_points = [
        PointStruct(id=generate_skill_point_id(sid), vector=emb.tolist(), payload=payload)
        for (sid, payload), emb in zip(skill_items, skill_embeddings)
    ]
    upserted_skills = upsert_points_in_batches(qdrant_client, SKILL_COLLECTION_NAME, skill_points, batch_size=batch_size)
    print(f"    Upserted {upserted_skills} points to '{SKILL_COLLECTION_NAME}'.")

    if sync_tutor_skills:
        upsert_points_in_batches(qdrant_client, TUTOR_SKILL_COLLECTION_NAME, skill_points, batch_size=batch_size)
        print(f"    Synced {upserted_skills} points to '{TUTOR_SKILL_COLLECTION_NAME}'.")

    # 7. Verification
    print("\n[7] Verifying collection point counts...")
    c_count = qdrant_client.count(collection_name=COURSE_COLLECTION_NAME).count
    s_count = qdrant_client.count(collection_name=SKILL_COLLECTION_NAME).count
    print(f"    '{COURSE_COLLECTION_NAME}': {c_count} points")
    print(f"    '{SKILL_COLLECTION_NAME}':  {s_count} points")

    if test_search:
        print("\n[8] Running sample semantic search queries...")
        for query_text, coll in [
            ("Lập trình Python và AI", COURSE_COLLECTION_NAME),
            ("machine learning and deep learning", SKILL_COLLECTION_NAME),
        ]:
            q_emb = model.encode([query_text], normalize_embeddings=True)[0].tolist()
            res = qdrant_client.query_points(collection_name=coll, query=q_emb, limit=2, with_payload=True)
            print(f"Query [{coll}]: '{query_text}'")
            for p in res.points:
                name = p.payload.get("title") or p.payload.get("skill")
                print(f"  -> [{round(p.score, 4)}] {name}")

    print("\n=======================================================")
    print("         POSTGRESQL INGESTION COMPLETED!               ")
    print("=======================================================\n")
    return 0


# ==========================================
# CLI ENTRYPOINT
# ==========================================
def main() -> None:
    parser = argparse.ArgumentParser(description="EduMentor AI Qdrant Data Ingestion - Pure PostgreSQL")
    parser.add_argument("--qdrant-url", type=str, default=None, help="Qdrant URL (defaults to QDRANT_URL env)")
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE, help="Batch size for encoding & upserting")
    parser.add_argument("--test-search", action="store_true", help="Run semantic search tests after ingestion")
    parser.add_argument("--no-clear", action="store_true", help="Skip clearing existing points")
    parser.add_argument("--no-tutor-sync", action="store_true", help="Skip syncing to tutor_skills collection")

    args = parser.parse_args()

    try:
        exit_code = run_ingestion(
            qdrant_url=args.qdrant_url,
            batch_size=args.batch_size,
            test_search=args.test_search,
            sync_tutor_skills=not args.no_tutor_sync,
            clear_points=not args.no_clear,
        )
        sys.exit(exit_code)
    except Exception as e:
        logger.exception("Ingestion failed")
        print(f"\n[ERROR] Ingestion failed: {e}\n", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
