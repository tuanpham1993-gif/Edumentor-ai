"""
EduMentor AI - Data Ingestion Service
Rebuilds Qdrant vector databases for Courses and Skills from raw JSON datasets.

Collections:
- edumentor_courses: Vector representation of courses (title, level, org, skills, description)
- edumentor_skills: Vector representation of skills enriched with related course context

Embedding Model:
- sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 (dim=384, cosine)
"""

import argparse
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any
from uuid import NAMESPACE_URL, uuid5

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
from sentence_transformers import SentenceTransformer

# Setup basic logging
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
SKILL_COLLECTION_NAME = "tutor_skills"

# Stable Point ID Generators
def generate_course_point_id(course_id: int) -> str:
    """Generate deterministic UUID for course point based on course_id."""
    return str(uuid5(NAMESPACE_URL, f"edumentor-course:{course_id}"))


def generate_skill_point_id(skill_id: int) -> str:
    """Generate deterministic UUID for skill point based on skill_id."""
    return str(uuid5(NAMESPACE_URL, f"edumentor-skill:{skill_id}"))


# ==========================================
# PATH RESOLUTION & DATA LOADING
# ==========================================
def find_data_dir() -> Path:
    """
    Locates the directory containing the 4 JSON datasets.
    Supports DATA_DIR env var, Docker paths (/app/datajson, /app/data),
    and local development paths.
    """
    env_dir = os.environ.get("DATA_DIR")
    if env_dir:
        p = Path(env_dir)
        if p.is_dir():
            return p

    current_file_dir = Path(__file__).resolve().parent  # backend/scripts
    backend_dir = current_file_dir.parent               # backend
    project_root = backend_dir.parent                  # repo root

    candidate_dirs = [
        Path("/app/datajson"),
        Path("/app/data"),
        project_root / "datajson",
        project_root / "data",
        backend_dir / "datajson",
        backend_dir / "data",
        Path("datajson"),
        Path("../datajson"),
        Path("data"),
        Path("../data"),
    ]

    for candidate in candidate_dirs:
        if candidate.is_dir():
            has_course = (candidate / "course_table.json").is_file() or (candidate / "courses.json").is_file()
            has_skill = (candidate / "skill_table.json").is_file() or (candidate / "skills.json").is_file()
            if has_course and has_skill:
                return candidate.resolve()

    raise FileNotFoundError(
        f"Could not locate data directory with course and skill JSON files. "
        f"Checked candidates: {[str(c) for c in candidate_dirs]}"
    )


def load_single_json(directory: Path, primary_name: str, fallback_name: str) -> tuple[list[dict[str, Any]], str]:
    """Loads a JSON file with primary or fallback name from directory."""
    p1 = directory / primary_name
    if p1.is_file():
        with open(p1, "r", encoding="utf-8") as f:
            return json.load(f), primary_name

    p2 = directory / fallback_name
    if p2.is_file():
        with open(p2, "r", encoding="utf-8") as f:
            return json.load(f), fallback_name

    raise FileNotFoundError(
        f"Neither '{primary_name}' nor '{fallback_name}' found in {directory}"
    )


def load_all_datasets(data_dir: Path) -> dict[str, Any]:
    """Loads all 4 datasets from the target directory."""
    courses_raw, c_name = load_single_json(data_dir, "course_table.json", "courses.json")
    skills_raw, s_name = load_single_json(data_dir, "skill_table.json", "skills.json")
    cs_raw, cs_name = load_single_json(data_dir, "course_skill_relation.json", "course_skills.json")
    sr_raw, sr_name = load_single_json(data_dir, "skill_relation.json", "skill_relationships.json")

    return {
        "courses": courses_raw,
        "skills": skills_raw,
        "course_skills": cs_raw,
        "skill_relations": sr_raw,
        "filenames": {
            "courses": c_name,
            "skills": s_name,
            "course_skills": cs_name,
            "skill_relations": sr_name,
        },
    }


# ==========================================
# VALIDATION
# ==========================================
def validate_datasets(datasets: dict[str, Any]) -> dict[str, Any]:
    """
    Validates integrity of the 4 datasets:
    - Unique IDs
    - Presence of required fields
    - Foreign key referential integrity
    Returns organized mappings for embedding construction.
    """
    courses_raw = datasets["courses"]
    skills_raw = datasets["skills"]
    cs_raw = datasets["course_skills"]
    sr_raw = datasets["skill_relations"]

    if not isinstance(courses_raw, list) or not courses_raw:
        raise ValueError("courses dataset must be a non-empty list.")
    if not isinstance(skills_raw, list) or not skills_raw:
        raise ValueError("skills dataset must be a non-empty list.")

    # 1. Validate Courses
    courses_by_id: dict[int, dict[str, Any]] = {}
    missing_course_id = 0
    missing_course_title = 0

    for idx, c in enumerate(courses_raw):
        cid = c.get("course_id")
        if cid is None:
            missing_course_id += 1
            continue
        try:
            cid = int(cid)
        except (ValueError, TypeError):
            missing_course_id += 1
            continue

        if cid in courses_by_id:
            logger.warning(f"Duplicate course_id detected: {cid}. Overwriting.")

        if not c.get("title"):
            missing_course_title += 1

        courses_by_id[cid] = c

    if missing_course_id > 0:
        logger.warning(f"Found {missing_course_id} course records with missing/invalid course_id.")
    if missing_course_title > 0:
        logger.warning(f"Found {missing_course_title} course records with empty title.")

    # 2. Validate Skills
    skills_by_id: dict[int, dict[str, Any]] = {}
    missing_skill_id = 0
    missing_skill_name = 0

    for idx, s in enumerate(skills_raw):
        sid = s.get("skill_id")
        if sid is None:
            missing_skill_id += 1
            continue
        try:
            sid = int(sid)
        except (ValueError, TypeError):
            missing_skill_id += 1
            continue

        sname = s.get("skill")
        if not sname or not str(sname).strip():
            missing_skill_name += 1

        skills_by_id[sid] = s

    if missing_skill_id > 0:
        logger.warning(f"Found {missing_skill_id} skill records with missing/invalid skill_id.")
    if missing_skill_name > 0:
        logger.warning(f"Found {missing_skill_name} skill records with empty skill name.")

    # 3. Validate Course-Skill Relations & Build Bi-directional Mappings
    course_to_skills: dict[int, list[str]] = {}
    skill_to_courses: dict[int, list[dict[str, Any]]] = {}
    invalid_cs_cid = 0
    invalid_cs_sid = 0

    for cs in cs_raw:
        cid = cs.get("course_id")
        sid = cs.get("skill_id")
        sname = cs.get("skill")

        try:
            cid = int(cid) if cid is not None else None
            sid = int(sid) if sid is not None else None
        except (ValueError, TypeError):
            continue

        if cid is None or cid not in courses_by_id:
            invalid_cs_cid += 1
            continue
        if sid is None or sid not in skills_by_id:
            invalid_cs_sid += 1
            continue

        skill_text = sname or skills_by_id[sid].get("skill") or ""
        if skill_text:
            course_to_skills.setdefault(cid, []).append(skill_text)

        course_obj = courses_by_id[cid]
        skill_to_courses.setdefault(sid, []).append(course_obj)

    # 4. Validate Skill Relationships
    invalid_sr_refs = 0
    for sr in sr_raw:
        fid = sr.get("from_skill_id")
        tid = sr.get("to_skill_id")
        try:
            fid = int(fid) if fid is not None else None
            tid = int(tid) if tid is not None else None
        except (ValueError, TypeError):
            invalid_sr_refs += 1
            continue
        if fid not in skills_by_id or tid not in skills_by_id:
            invalid_sr_refs += 1

    return {
        "courses_by_id": courses_by_id,
        "skills_by_id": skills_by_id,
        "course_to_skills": course_to_skills,
        "skill_to_courses": skill_to_courses,
        "stats": {
            "valid_courses": len(courses_by_id),
            "valid_skills": len(skills_by_id),
            "valid_course_skills": len(cs_raw) - invalid_cs_cid - invalid_cs_sid,
            "valid_skill_relations": len(sr_raw) - invalid_sr_refs,
            "skills_with_courses": len(skill_to_courses),
            "skills_without_courses": len(skills_by_id) - len(skill_to_courses),
        },
    }


# ==========================================
# EMBEDDING TEXT BUILDERS WITH TOKEN CONTROL
# ==========================================
def build_course_embedding_text(
    course: dict[str, Any],
    related_skills: list[str],
    tokenizer: Any,
    max_tokens: int = MAX_SEQ_LENGTH,
) -> str:
    """
    Builds Course embedding text following Section 4:
    Course: [title]

    Description:
    [description]

    Level:
    [level]

    Organization:
    [organization]

    Related Skills:
    [Danh sách Skill liên kết thực tế]

    Strictly manages token length with tokenizer to never exceed max_tokens.
    """
    title = str(course.get("title") or "").strip()
    level = str(course.get("level") or "N/A").strip()
    org = str(course.get("organization") or "N/A").strip()
    desc = str(course.get("description") or "").strip()

    # Deduplicate skills preserving order
    unique_skills = list(dict.fromkeys(related_skills))
    skills_str = ", ".join(unique_skills) if unique_skills else "N/A"

    prefix = f"Course: {title}\n\nDescription:\n"
    suffix = f"\n\nLevel:\n{level}\n\nOrganization:\n{org}\n\nRelated Skills:\n{skills_str}"

    prefix_tokens = tokenizer(prefix, add_special_tokens=False, truncation=False)["input_ids"]
    suffix_tokens = tokenizer(suffix, add_special_tokens=False, truncation=False)["input_ids"]
    fixed_token_count = len(prefix_tokens) + len(suffix_tokens) + 2  # +2 for CLS and SEP

    # If fixed fields exceed token limit, trim skills until it fits
    if fixed_token_count >= max_tokens:
        trimmed_skills = list(unique_skills)
        while trimmed_skills and fixed_token_count >= max_tokens:
            trimmed_skills.pop()
            skills_str = ", ".join(trimmed_skills) if trimmed_skills else "N/A"
            suffix = f"\n\nLevel:\n{level}\n\nOrganization:\n{org}\n\nRelated Skills:\n{skills_str}"
            suffix_tokens = tokenizer(suffix, add_special_tokens=False, truncation=False)["input_ids"]
            fixed_token_count = len(prefix_tokens) + len(suffix_tokens) + 2
        desc_token_budget = max(0, max_tokens - fixed_token_count)
    else:
        desc_token_budget = max_tokens - fixed_token_count

    # Truncate description to fit exactly in remaining token budget
    if desc and desc_token_budget > 0:
        desc_tokens = tokenizer(desc, add_special_tokens=False, truncation=False)["input_ids"]
        if len(desc_tokens) > desc_token_budget:
            truncated_desc = tokenizer.decode(desc_tokens[:desc_token_budget], skip_special_tokens=True).strip()
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
    """
    Builds Skill embedding text following Section 5:
    Skill: [Skill name]

    Related Courses:

    1. [Course Title]

    Description:
    [Course Description]

    2. ...

    If skill has no related courses:
    Skill: [Skill name]
    """
    skill_name = str(skill_name or "").strip()
    if not related_courses:
        return f"Skill: {skill_name}"

    header = f"Skill: {skill_name}\n\nRelated Courses:\n\n"
    header_tokens = tokenizer(header, add_special_tokens=False, truncation=False)["input_ids"]
    budget = max_tokens - len(header_tokens) - 2

    if budget <= 0:
        return f"Skill: {skill_name}"

    body_parts = []
    # Deduplicate courses by course_id
    seen_cids = set()
    unique_courses = []
    for c in related_courses:
        cid = c.get("course_id")
        if cid not in seen_cids:
            seen_cids.add(cid)
            unique_courses.append(c)

    for idx, c in enumerate(unique_courses, start=1):
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
            budget = 0
            break
        else:
            body_parts.append(f"{c_prefix}{cdesc}\n\n")
            budget -= (len(c_prefix_tokens) + len(cdesc_tokens))
            if budget <= 10:
                break

    body = "".join(body_parts).strip()
    if not body:
        return f"Skill: {skill_name}"

    return f"{header}{body}".strip()


# ==========================================
# QDRANT OPERATIONS
# ==========================================
def wait_for_qdrant(qdrant_url: str, timeout_seconds: int = 60) -> QdrantClient:
    """Waits until Qdrant is responsive and healthy."""
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

    raise ConnectionError(f"Failed to connect to Qdrant at {qdrant_url} within {timeout_seconds}s. Error: {last_err}")


def ensure_collection(client: QdrantClient, collection_name: str, vector_size: int = EMBEDDING_DIMENSION) -> None:
    """
    Ensures a Qdrant collection exists with proper VectorParams.
    If already exists, validates configuration without deleting it.
    """
    collections = client.get_collections().collections
    existing_names = {c.name for c in collections}

    if collection_name in existing_names:
        info = client.get_collection(collection_name)
        existing_size = info.config.params.vectors.size
        existing_distance = info.config.params.vectors.distance
        if existing_size != vector_size or existing_distance != Distance.COSINE:
            raise ValueError(
                f"Collection '{collection_name}' exists but has mismatching configuration: "
                f"size={existing_size} (expected {vector_size}), distance={existing_distance} (expected COSINE)."
            )
        logger.info(f"Collection '{collection_name}' already exists and is valid.")
        return

    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=vector_size,
            distance=Distance.COSINE,
        ),
    )
    logger.info(f"Created collection '{collection_name}' (size={vector_size}, distance=COSINE).")


def upsert_points_in_batches(
    client: QdrantClient,
    collection_name: str,
    points: list[PointStruct],
    batch_size: int = DEFAULT_BATCH_SIZE,
) -> int:
    """Upserts points into Qdrant collection in batches."""
    total = len(points)
    for start in range(0, total, batch_size):
        batch = points[start : start + batch_size]
        client.upsert(
            collection_name=collection_name,
            points=batch,
            wait=True,
        )
    return total


# ==========================================
# MAIN INGESTION PIPELINE
# ==========================================
def run_ingestion(
    qdrant_url: str | None = None,
    data_dir_override: str | None = None,
    batch_size: int = DEFAULT_BATCH_SIZE,
    test_search: bool = False,
) -> int:
    """
    Executes the full EduMentor AI Data Ingestion pipeline.
    """
    qdrant_url = qdrant_url or os.environ.get("QDRANT_URL", "http://localhost:6335")

    print("\n========== EDUMENTOR DATA INGESTION ==========\n")

    # [1] Loading JSON datasets...
    print("[1] Loading JSON datasets...")
    data_dir = Path(data_dir_override) if data_dir_override else find_data_dir()
    print(f"    Source directory: {data_dir}")
    datasets = load_all_datasets(data_dir)
    print(f"    Loaded: {datasets['filenames']['courses']} ({len(datasets['courses'])} records)")
    print(f"    Loaded: {datasets['filenames']['skills']} ({len(datasets['skills'])} records)")
    print(f"    Loaded: {datasets['filenames']['course_skills']} ({len(datasets['course_skills'])} relations)")
    print(f"    Loaded: {datasets['filenames']['skill_relations']} ({len(datasets['skill_relations'])} relations)")

    # [2] Validating source records...
    print("[2] Validating source records...")
    validated = validate_datasets(datasets)
    stats = validated["stats"]
    print(f"    Valid Courses: {stats['valid_courses']}")
    print(f"    Valid Skills: {stats['valid_skills']}")
    print(f"    Skills with linked courses: {stats['skills_with_courses']}")
    print(f"    Skills without linked courses: {stats['skills_without_courses']}")

    # [5] Loading embedding model early for tokenizer in steps [3] & [4]
    print("[5] Loading embedding model...")
    print(f"    Model: {EMBEDDING_MODEL_NAME}")
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    tokenizer = model.tokenizer
    print(f"    Tokenizer max_seq_length: {model.max_seq_length}, Dimension: {EMBEDDING_DIMENSION}")

    # [3] Building Course embedding texts...
    print("[3] Building Course embedding texts...")
    course_items = []
    course_texts = []
    for cid, c in validated["courses_by_id"].items():
        skills = validated["course_to_skills"].get(cid, [])
        text = build_course_embedding_text(c, skills, tokenizer, max_tokens=MAX_SEQ_LENGTH)
        payload = {
            "course_id": cid,
            "title": str(c.get("title") or ""),
            "level": str(c.get("level") or "N/A"),
            "organization": str(c.get("organization") or "N/A"),
            "instructor": str(c.get("instructor") or "N/A"),
            "url": str(c.get("url") or ""),
            "num_skills": len(skills),
        }
        course_items.append((cid, payload))
        course_texts.append(text)
    print(f"    Built {len(course_texts)} course texts.")

    # [4] Building Skill embedding texts...
    print("[4] Building Skill embedding texts...")
    skill_items = []
    skill_texts = []
    for sid, s in validated["skills_by_id"].items():
        sname = str(s.get("skill") or "")
        related_courses = validated["skill_to_courses"].get(sid, [])
        text = build_skill_embedding_text(sname, related_courses, tokenizer, max_tokens=MAX_SEQ_LENGTH)
        payload = {
            "skill_id": sid,
            "skill": sname,
            "num_courses": len(related_courses),
        }
        skill_items.append((sid, payload))
        skill_texts.append(text)
    print(f"    Built {len(skill_texts)} skill texts.")

    # [6] Creating/checking Qdrant collections...
    print("[6] Creating/checking Qdrant collections...")
    qdrant_client = wait_for_qdrant(qdrant_url)
    ensure_collection(qdrant_client, COURSE_COLLECTION_NAME, vector_size=EMBEDDING_DIMENSION)
    ensure_collection(qdrant_client, SKILL_COLLECTION_NAME, vector_size=EMBEDDING_DIMENSION)

    # [7] Upserting Course vectors...
    print("[7] Upserting Course vectors...")
    logger.info("Encoding course texts into embeddings...")
    course_embeddings = model.encode(
        course_texts,
        batch_size=batch_size,
        normalize_embeddings=True,
        show_progress_bar=False,
    )
    course_points = [
        PointStruct(
            id=generate_course_point_id(cid),
            vector=embedding.tolist(),
            payload=payload,
        )
        for (cid, payload), embedding in zip(course_items, course_embeddings)
    ]
    upserted_courses = upsert_points_in_batches(
        qdrant_client,
        COURSE_COLLECTION_NAME,
        course_points,
        batch_size=batch_size,
    )
    print(f"    Upserted {upserted_courses} course points into '{COURSE_COLLECTION_NAME}'.")

    # [8] Upserting Skill vectors...
    print("[8] Upserting Skill vectors...")
    logger.info("Encoding skill texts into embeddings...")
    skill_embeddings = model.encode(
        skill_texts,
        batch_size=batch_size,
        normalize_embeddings=True,
        show_progress_bar=False,
    )
    skill_points = [
        PointStruct(
            id=generate_skill_point_id(sid),
            vector=embedding.tolist(),
            payload=payload,
        )
        for (sid, payload), embedding in zip(skill_items, skill_embeddings)
    ]
    upserted_skills = upsert_points_in_batches(
        qdrant_client,
        SKILL_COLLECTION_NAME,
        skill_points,
        batch_size=batch_size,
    )
    print(f"    Upserted {upserted_skills} skill points into '{SKILL_COLLECTION_NAME}'.")

    # [9] Verifying Qdrant collections...
    print("[9] Verifying Qdrant collections...")
    course_count = qdrant_client.count(collection_name=COURSE_COLLECTION_NAME).count
    skill_count = qdrant_client.count(collection_name=SKILL_COLLECTION_NAME).count
    print(f"    Verified '{COURSE_COLLECTION_NAME}' point count: {course_count}")
    print(f"    Verified '{SKILL_COLLECTION_NAME}' point count: {skill_count}")

    # Optional semantic search test
    if test_search:
        print("\n--- Testing Semantic Search (Vietnamese & English) ---")
        test_queries = [
            ("Lập trình Python và trí tuệ nhân tạo cho người mới bắt đầu", COURSE_COLLECTION_NAME),
            ("Phát triển ứng dụng di động Android", COURSE_COLLECTION_NAME),
            ("machine learning", SKILL_COLLECTION_NAME),
            ("quản lý cơ sở dữ liệu quan hệ", SKILL_COLLECTION_NAME),
        ]
        for query_text, coll in test_queries:
            q_emb = model.encode([query_text], normalize_embeddings=True)[0].tolist()
            res = qdrant_client.query_points(
                collection_name=coll,
                query=q_emb,
                limit=2,
                with_payload=True,
            )
            print(f"Query [{coll}]: '{query_text}'")
            for p in res.points:
                score = round(p.score, 4)
                name = p.payload.get("title") or p.payload.get("skill")
                print(f"  -> score={score} | {name}")

    print("\n========== INGESTION RESULT ==========\n")
    print(f"Courses source records: {len(datasets['courses'])}")
    print(f"Courses indexed:        {course_count}")
    print()
    print(f"Skills source records:  {len(datasets['skills'])}")
    print(f"Skills indexed:         {skill_count}")
    print()
    print(f"Course collection:      {COURSE_COLLECTION_NAME}")
    print(f"Skill collection:       {SKILL_COLLECTION_NAME}")
    print("\nINGESTION COMPLETED SUCCESSFULLY\n")

    return 0


# ==========================================
# CLI ENTRYPOINT
# ==========================================
def main() -> None:
    parser = argparse.ArgumentParser(description="EduMentor AI Qdrant Data Ingestion")
    parser.add_argument("--qdrant-url", type=str, default=None, help="Qdrant service URL")
    parser.add_argument("--data-dir", type=str, default=None, help="Override path to data directory")
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE, help="Batch size for encoding & upserting")
    parser.add_argument("--test-search", action="store_true", help="Run semantic search tests after ingestion")

    args = parser.parse_args()

    try:
        exit_code = run_ingestion(
            qdrant_url=args.qdrant_url,
            data_dir_override=args.data_dir,
            batch_size=args.batch_size,
            test_search=args.test_search,
        )
        sys.exit(exit_code)
    except Exception as e:
        logger.exception("Ingestion failed with unhandled exception")
        print(f"\n[ERROR] Ingestion failed: {e}\n", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
