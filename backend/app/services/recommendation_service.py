from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models.skill import Skills
from app.recommender.build_learning_graph import generate_learning_path
from app.core.embedding_model import generate_embedding_skills_name
from app.services.qdrant_service import qdrant_skill_service

MIN_QDRANT_SCORE = 0.75

def normalize_skill_name(skill: str) -> str:
    return skill.strip().casefold()

def extract_target_skills(extracted_skills: list[str],db: Session) -> list[int]:
    target_skill_ids = []
    unmatched_skills = []

    for skill in extracted_skills:
        matched_skill_id = (
            db.query(Skills.skill_id)
            .filter(
                Skills.is_active.is_(True),
                func.lower(func.trim(Skills.skill))
                == skill.strip().lower()
            )
            .order_by(Skills.skill_id.asc())
            .limit(1)
            .scalar()
        )

        if matched_skill_id is not None:
            target_skill_ids.append(matched_skill_id)
        else:
            unmatched_skills.append(skill)

    if unmatched_skills:
        embeddings = generate_embedding_skills_name(unmatched_skills)
        for skill, embedding in zip(unmatched_skills, embeddings):
            results = qdrant_skill_service.search_skill(embedding,limit=5)
            if not results: continue
            best_match = next((
               result for result in results
                    if (result.score >= MIN_QDRANT_SCORE)
                    ),None)
            if best_match is None: continue
            target_skill_ids.append(best_match.payload["skill_id"]) 
    return list(dict.fromkeys(target_skill_ids))


# ======================================================
# 2. Enrich graph with skill names
# ======================================================

def enrich_learning_path_with_skill_names(
    db: Session,
    learning_path: dict,
) -> dict:
    """
    Add skill names to nodes and edges.

    This information is only for API presentation.
    It is not persisted in the database.
    """

    # Collect skill IDs from both nodes and edges.
    skill_ids = {
        node["skill_id"]
        for node in learning_path["nodes"]
    }

    for edge in learning_path["edges"]:
        skill_ids.add(edge["from_skill_id"])
        skill_ids.add(edge["to_skill_id"])

    if not skill_ids:
        raise ValueError("Generated learning path contains no skills.")

    # Retrieve skill information.
    statement = select(
        Skills.skill_id,
        Skills.skill,
    ).where(
        Skills.skill_id.in_(skill_ids)
    )

    results = db.execute(statement).all()

    skill_name_map = {
        skill_id: skill_name
        for skill_id, skill_name in results
    }

    # Check for missing skills.
    missing_skill_ids = skill_ids - skill_name_map.keys()

    if missing_skill_ids:
        raise ValueError(
            f"Skills not found in database: {sorted(missing_skill_ids)}"
        )

    # Enrich nodes.
    for node in learning_path["nodes"]:
        node["skill_name"] = skill_name_map[node["skill_id"]]

    # Enrich edges.
    for edge in learning_path["edges"]:
        edge["from_skill_name"] = skill_name_map[
            edge["from_skill_id"]
        ]

        edge["to_skill_name"] = skill_name_map[
            edge["to_skill_id"]
        ]

    return learning_path


# ======================================================
# 3. Generate learning path preview
# ======================================================

def generate_learning_path_preview(
    db: Session,
    original_query: str,
    target_skill_ids: list[int],
    goal_type: str,
) -> dict:
    """
    Generate a learning path preview without saving
    anything to the learning_paths tables.
    """

    # Step 2: Generate graph using existing pipeline.
    learning_path = generate_learning_path(
        db=db,
        LLM_input_skill_list=target_skill_ids,
        user_query=original_query,
        goal_type=goal_type,
        path_id=None,
    )

    # Step 3: Add skill names.
    learning_path = enrich_learning_path_with_skill_names(
        db=db,
        learning_path=learning_path,
    )

    return learning_path