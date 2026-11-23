"""
Query Router Package for EduMentor AI.
Modular query routing with rule-based and LLM-powered classification,
entity extraction, and query decomposition.
"""

from app.ai.query_router.config import (
    ALLOWED_ENTITY_TYPES,
    ALLOWED_INTENTS,
    COMMON_CODE_ERRORS,
    COMMON_TECH_SKILLS,
    ENTITY_REQUIRED_INTENTS,
    GENERIC_ENTITIES,
    INTENT_CATEGORY_MAP,
    RETRIEVAL_MAP,
    RETRIEVAL_STRATEGIES,
    ROUTE_CATEGORY_MAP,
    ROUTE_KEYWORDS,
    TASK_TYPES,
)
from app.ai.query_router.entity_extractor import (
    detect_entity_type,
    extract_course_enrollment_entity,
    extract_course_review_entity,
    extract_course_search_entity,
    extract_entity_by_llm,
    extract_entity_by_rules,
    extract_learning_path_entity,
    extract_skill_review_entity,
    extract_skill_search_entity,
)
from app.ai.query_router.intent_classifier import (
    build_classifier_prompt,
    classify_by_llm,
    classify_by_rules,
)
from app.ai.query_router.normalizer import (
    clean_entity_name,
    detect_operation_type,
    extract_json_object,
    finalize_entity,
    is_generic_entity,
    normalize_entity_name,
    normalize_text,
    remove_accents,
)
from app.ai.query_router.query_decomposer import (
    decompose_query_by_llm,
    may_contain_multiple_requests,
)
from app.ai.query_router.router import _route_single_query, route_query

__all__ = [
    "ALLOWED_ENTITY_TYPES",
    "ALLOWED_INTENTS",
    "COMMON_CODE_ERRORS",
    "COMMON_TECH_SKILLS",
    "ENTITY_REQUIRED_INTENTS",
    "GENERIC_ENTITIES",
    "INTENT_CATEGORY_MAP",
    "RETRIEVAL_MAP",
    "RETRIEVAL_STRATEGIES",
    "ROUTE_CATEGORY_MAP",
    "ROUTE_KEYWORDS",
    "TASK_TYPES",
    "_route_single_query",
    "build_classifier_prompt",
    "classify_by_llm",
    "classify_by_rules",
    "clean_entity_name",
    "decompose_query_by_llm",
    "detect_entity_type",
    "detect_operation_type",
    "extract_course_enrollment_entity",
    "extract_course_review_entity",
    "extract_course_search_entity",
    "extract_entity_by_llm",
    "extract_entity_by_rules",
    "extract_json_object",
    "extract_learning_path_entity",
    "extract_skill_review_entity",
    "extract_skill_search_entity",
    "finalize_entity",
    "is_generic_entity",
    "may_contain_multiple_requests",
    "normalize_entity_name",
    "normalize_text",
    "remove_accents",
    "route_query",
]
