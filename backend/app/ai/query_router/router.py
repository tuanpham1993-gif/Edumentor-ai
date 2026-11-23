"""
Main Query Router module.
Orchestrates rule classification, LLM classification, entity extraction,
query decomposition, and unified task_type / retrieval_strategy determination.
"""

from app.ai.query_router.config import (
    ENTITY_REQUIRED_INTENTS,
    STRATEGY_TO_MODES,
)
from app.ai.query_router.entity_extractor import (
    extract_entity_by_llm,
    extract_entity_by_rules,
)
from app.ai.query_router.intent_classifier import (
    classify_by_llm,
    classify_by_rules,
)
from app.ai.query_router.normalizer import (
    detect_operation_type,
    finalize_entity,
    is_generic_entity,
    normalize_text,
)
from app.ai.query_router.query_decomposer import (
    decompose_query_by_llm,
    may_contain_multiple_requests,
)


def _determine_task_type_and_strategy(
    intent: str,
    entity_type: str,
    entity_name: str | None,
    user_message: str = "",
) -> tuple[str, str, list[str]]:
    """
    Xác định task_type, retrieval_strategy và retrieval_modes đồng bộ hoàn toàn.
    """
    norm_msg = normalize_text(user_message) if user_message else ""
    is_relation_search = "lien quan" in norm_msg or "related" in norm_msg

    if intent == "course_search":
        if entity_type == "organization":
            strategy = "sql"
            task_type = "organization_search"
        elif entity_type == "rating":
            strategy = "sql"
            task_type = "rating_search"
        elif entity_name and not is_generic_entity(entity_name):
            strategy = "sql_qdrant"
            task_type = "course_name_search"
        else:
            strategy = "qdrant"
            task_type = "course_semantic_search"
        return task_type, strategy, STRATEGY_TO_MODES[strategy].copy()

    if intent == "skill_search":
        # Popular skill query or relation query should use semantic Qdrant search.
        if entity_type == "popular" or is_relation_search:
            strategy = "qdrant"
            task_type = "skill_semantic_search"
        elif entity_name and not is_generic_entity(entity_name):
            # Specific skill name provided → use combined SQL + Qdrant name search.
            strategy = "sql_qdrant"
            task_type = "skill_name_search"
        else:
            # Fallback to semantic search.
            strategy = "qdrant"
            task_type = "skill_semantic_search"
        return task_type, strategy, STRATEGY_TO_MODES[strategy].copy()

    if intent == "course_question":
        strategy = "sql_gemini" if entity_name else "gemini"
        return "knowledge_question", strategy, STRATEGY_TO_MODES[strategy].copy()

    if intent == "skill_question":
        strategy = "sql_gemini" if entity_name else "gemini"
        return "knowledge_question", strategy, STRATEGY_TO_MODES[strategy].copy()

    if intent == "course_review":
        strategy = "sql_gemini"
        return "course_review_search", strategy, STRATEGY_TO_MODES[strategy].copy()

    if intent in ("skill_review", "reinforcement_request"):
        strategy = "sql_gemini" if entity_name else "gemini"
        return "reinforcement_request", strategy, STRATEGY_TO_MODES[strategy].copy()

    if intent == "code_analysis":
        strategy = "gemini"
        return "code_analysis", strategy, STRATEGY_TO_MODES[strategy].copy()

    if intent == "code_fix":
        strategy = "gemini"
        return "code_fix", strategy, STRATEGY_TO_MODES[strategy].copy()

    if intent == "code_help":
        strategy = "gemini"
        return "code_analysis", strategy, STRATEGY_TO_MODES[strategy].copy()

    if intent == "learning_path_request":
        strategy = "sql_gemini" if entity_name else "gemini"
        return "learning_path_request", strategy, STRATEGY_TO_MODES[strategy].copy()

    if intent == "system_operation":
        strategy = "gemini"
        return "system_operation", strategy, STRATEGY_TO_MODES[strategy].copy()

    if intent == "course_enrollment_link":
        strategy = "sql"
        return "course_name_search", strategy, STRATEGY_TO_MODES[strategy].copy()

    # Default / general_question
    strategy = "gemini"
    return "knowledge_question", strategy, STRATEGY_TO_MODES[strategy].copy()


def _route_single_query(user_message: str, custom_api_key: str | None = None) -> dict:
    """
    Xử lý một yêu cầu đơn lẻ.
    """
    result = classify_by_rules(user_message)

    if result is not None:
        source = "rule"
    else:
        try:
            result = classify_by_llm(user_message, custom_api_key=custom_api_key)
            source = "llm"
        except Exception as error:  # noqa: BLE001
            print("[QUERY ROUTER] LLM classification failed:", str(error))
            result = {
                "intent": "general_question",
                "entity_type": "none",
                "entity_name": None,
            }
            source = "fallback"

    intent = result["intent"]

    # Step 1. Rule-based entity extraction
    entity = extract_entity_by_rules(user_message=user_message, intent=intent)
    entity_type = result.get("entity_type", "none")
    entity_name = result.get("entity_name")

    if entity.get("entity_name"):
        entity_name = entity["entity_name"]
        entity_type = entity["entity_type"]

    # Step 2. Optional LLM entity extraction
    normalized_input = normalize_text(user_message)
    is_continuation_query = any(
        m in normalized_input
        for m in [
            "con nua khong",
            "con khac khong",
            "nua khong",
            "khac khong",
            "con gi nua",
            "co cai nao nua",
            "co cai nao khac",
            "con khoa hoc nao",
            "khoa hoc nao nua",
            "khoa hoc nao khac",
            "con ky nang nao",
            "ky nang nao nua",
            "ky nang nao khac",
            "cho them",
            "vi du khac",
            "cau hoi khac",
            "bai khac",
        ]
    )

    if intent in ENTITY_REQUIRED_INTENTS and entity_name is None and not is_continuation_query:
        try:
            llm_entity = extract_entity_by_llm(user_message, custom_api_key=custom_api_key)
            if llm_entity.get("entity_name"):
                entity_name = llm_entity["entity_name"]
                entity_type = llm_entity["entity_type"]
                source = "hybrid"
        except Exception as error:  # noqa: BLE001
            print("[QUERY ROUTER] Entity extraction failed:", str(error))

    entity_name = finalize_entity(entity_name)

    # Step 3. Enforce entity type
    if intent in {"skill_question", "skill_review", "reinforcement_request"}:
        entity_type = "skill"
    elif intent == "skill_search":
        if entity_type != "popular":
            entity_type = "skill"
    elif intent == "course_search":
        if entity_type not in {"organization", "instructor", "rating", "level", "popular"}:
            entity_type = "skill"
    elif intent in {"course_question", "course_review", "course_enrollment_link"}:
        entity_type = "course"
    elif intent == "learning_path_request":
        entity_type = "skill" if entity_name else "none"
    elif intent in {"code_help", "code_analysis", "code_fix"}:
        entity_type = "skill" if entity_name else "none"
    else:
        entity_type = "none"
        entity_name = None

    if is_generic_entity(entity_name):
        entity_name = None
        if intent == "learning_path_request":
            entity_type = "none"

    # Step 4. Unified Task Type, Strategy and Modes
    task_type, retrieval_strategy, retrieval_modes = _determine_task_type_and_strategy(
        intent=intent,
        entity_type=entity_type,
        entity_name=entity_name,
        user_message=user_message,
    )

    # Step 5. Operation type
    operation_type = None
    if intent == "system_operation":
        operation_type = detect_operation_type(user_message)

    return {
        "intent": intent,
        "task_type": task_type,
        "retrieval_strategy": retrieval_strategy,
        "operation_type": operation_type,
        "retrieval_modes": retrieval_modes,
        "entity_type": entity_type,
        "entity_name": entity_name,
        "source": source,
        "query": user_message,
    }


def route_query(user_message: str, custom_api_key: str | None = None) -> dict:
    """
    Router tổng.

    Pipeline:
    1. Validate input.
    2. Kiểm tra câu phức hợp (multi-query).
    3. Phân tách câu hỏi nếu cần (truyền custom_api_key).
    4. Định tuyến từng sub-query (truyền custom_api_key).
    5. Gán task_type, retrieval_strategy, entity.
    6. Trả về kết quả tương thích ngược với format cũ.
    """
    if not isinstance(user_message, str) or not user_message.strip():
        raise ValueError("Câu hỏi không được để trống.")

    user_message = user_message.strip()
    queries = [user_message]

    if may_contain_multiple_requests(user_message):
        try:
            queries = decompose_query_by_llm(user_message, custom_api_key=custom_api_key)
        except Exception as error:  # noqa: BLE001
            print("[QUERY ROUTER] Decomposition failed:", str(error))
            queries = [user_message]

    sub_queries = []
    for query in queries:
        try:
            route = _route_single_query(query, custom_api_key=custom_api_key)
        except Exception as error:  # noqa: BLE001
            print("[QUERY ROUTER] Single query routing failed:", str(error))
            route = {
                "intent": "general_question",
                "task_type": "knowledge_question",
                "retrieval_strategy": "gemini",
                "operation_type": None,
                "retrieval_modes": ["gemini"],
                "entity_type": "none",
                "entity_name": None,
                "source": "fallback",
                "query": query,
            }

        sub_queries.append({
            "query": query,
            "intent": route["intent"],
            "task_type": route.get("task_type", "knowledge_question"),
            "retrieval_strategy": route.get("retrieval_strategy", "gemini"),
            "operation_type": route.get("operation_type"),
            "retrieval_modes": route["retrieval_modes"],
            "entity_type": route["entity_type"],
            "entity_name": route["entity_name"],
            "source": route["source"],
        })

    # Combine retrieval modes
    all_modes = []
    for item in sub_queries:
        for mode in item["retrieval_modes"]:
            if mode not in all_modes:
                all_modes.append(mode)

    primary = sub_queries[0]

    return {
        "intent": primary["intent"],
        "task_type": primary.get("task_type", "knowledge_question"),
        "retrieval_strategy": primary.get("retrieval_strategy", "gemini"),
        "operation_type": primary["operation_type"],
        "retrieval_modes": all_modes,
        "entity_type": primary["entity_type"],
        "entity_name": primary["entity_name"],
        "source": primary["source"],
        "query": user_message,
        "is_compound": len(sub_queries) > 1,
        "sub_queries": sub_queries,
    }
