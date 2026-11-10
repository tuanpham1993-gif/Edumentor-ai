from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from sqlalchemy import Select, func, select, case
from sqlalchemy.orm import Session, selectinload
from app.models.learning_path import LearningPath
from app.core.embedding_model import model

def retrieve_historical_paths(
    db: Session,
    current_query: str,
    model,
    threshold: float = 0.7
    ):
    # 1. Exclude abandoned paths.
    #this part here need to be search from database #search goal type = template
    statement = select(LearningPath).where(
        LearningPath.status != "abandoned",
        LearningPath.goal_type == "template"
    ).options(selectinload(LearningPath.nodes))
    eligible_records = db.execute(statement).scalars().all()
    if not eligible_records: return []

    # 2. Encode current goal.
    current_embedding = model.encode([current_query],convert_to_numpy=True)

    # 3. Encode historical goals.
    historical_queries = [
        record.original_query for record in eligible_records
    ]

    historical_embeddings = model.encode(historical_queries, convert_to_numpy=True)
    # 4. Calculate cosine similarity.
    similarities = cosine_similarity(current_embedding,historical_embeddings)[0]
    # 5. Filter matching paths.
    matched_paths = []
    for record, similarity in zip(eligible_records, similarities):
        if similarity >= threshold:
            matched_paths.append({
                "record_id": record.record_id,
                "status": record.status,
                "similarity": float(similarity),
                "weight": float(similarity - threshold),
                "nodes": [
                    {
                        "skill_id": node.skill_id,
                        "node_role": node.node_role
                    } for node in record.nodes if node.node_role != "prerequisite"
                ]
            })

    return matched_paths

def calculate_skill_scores(matched_paths: list[dict]):
    """
    Calculate weighted skill frequency using skill_id.
    Each skill is counted only once per historical path.
    Prerequisite nodes are excluded.
    """

    total_weight = sum(path["weight"] for path in matched_paths)
    if not matched_paths or total_weight <= 0: return {}
    skill_weighted_frequency = {}

    for path in matched_paths:
        weight = path["weight"]
        unique_skill_ids = {node["skill_id"] for node in path["nodes"] if node["node_role"] != "prerequisite"}

        for skill_id in unique_skill_ids:
            skill_weighted_frequency[skill_id] = (skill_weighted_frequency.get(skill_id, 0) + weight)

    skill_scores = {
        skill_id: weighted_frequency / total_weight
        for skill_id, weighted_frequency in skill_weighted_frequency.items()
    }
    return skill_scores

def rank_extension_candidates(skill_scores: dict[int, float], 
                              current_graph_skill_ids: set[int],
                              min_skill_score: float = 0.1):
    candidates = []
    for skill_id, score in skill_scores.items():
        if skill_id not in current_graph_skill_ids and score > min_skill_score:
            candidates.append({"skill_id": skill_id, "skill_score": score})

    # Highest score first.
    candidates.sort(key=lambda item: item["skill_score"], reverse=True)
    return candidates


def historical_record_retrieval_pipeline(
    db: Session, current_query: str, 
    model, visited_skill_ids: set[int],
    threshold: float = 0.7):
    """Retrieve historical paths and extract extension skill candidates."""
    matched_paths = retrieve_historical_paths(
        db=db, current_query=current_query, 
        model=model, threshold=threshold
    )
    skill_score_dict = calculate_skill_scores(matched_paths)
    candidates = rank_extension_candidates( skill_scores=skill_score_dict, 
                                           current_graph_skill_ids=visited_skill_ids)
    return candidates