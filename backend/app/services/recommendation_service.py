from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.skill import Skills
from app.recommender.build_learning_graph import generate_learning_path


# ======================================================
# 1. Mock target skill extraction
# ======================================================

def extract_target_skills(original_query: str) -> list[int]:
    """
    Temporary mock implementation.

    Eventually, replace this function with the QLoRA
    skill extraction model.

    The frontend does not provide target_skill_ids.
    """
    goal_type = "career"
    return [486, 773, 87], goal_type


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
    #goal_type: str,
) -> dict:
    """
    Generate a learning path preview without saving
    anything to the learning_paths tables.
    """

    # Step 1: Extract target skills.
    target_skill_ids, goal_type = extract_target_skills(original_query)

    if not target_skill_ids:
        raise ValueError( "No target skills could be extracted from the learning goal." )

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