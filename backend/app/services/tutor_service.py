import json
from uuid import UUID

from sqlalchemy.orm import Session

from app.ai.orchestrator import orchestrator
from app.models.chat_message import ChatMessage
from app.services.rag_service import retrieve_knowledge
from app.services.sql_retrieval import retrieve_for_query


# ==========================================
# 1. CONFIGURATION
# ==========================================

RAG_TOP_K = 12


# ==========================================
# 2. BUILD RETRIEVAL CONTEXT
# ==========================================

def build_expanded_rag_query(
    user_content: str,
    route_result: dict,
) -> tuple[str, str | None, str | None]:
    """
    Không còn mở rộng query theo system.en.md hoặc route hệ thống.
    Giữ nguyên câu hỏi để tìm kiếm kiến thức Course/Skill.
    """
    intent = route_result.get("intent")
    target_category = {
        "course_question": "course_catalog",
        "course_review": "course_catalog",
        "course_search": "course_catalog",
    }.get(intent)

    return user_content, None, target_category


def rerank_rag_results(
    results: list[dict],
    target_route: str | None = None,
    target_category: str | None = None,
    intent: str | None = None,
) -> list[dict]:
    """Ưu tiên kết quả có category phù hợp; không phụ thuộc route tài liệu."""
    if not results:
        return []

    for item in results:
        metadata = item.get("metadata") or {}
        score = item.get("score") or 0
        if target_category and metadata.get("category") == target_category:
            score += 0.30
        item["rerank_score"] = score

    return sorted(
        results,
        key=lambda item: item.get("rerank_score", 0),
        reverse=True,
    )


def filter_relevant_rag_results(
    results: list[dict],
    intent: str | None = None,
    target_category: str | None = None,
) -> list[dict]:
    """Giữ kết quả RAG tổng quát; không lọc theo tài liệu system.en.md."""
    return results


def build_retrieval_context(

    db: Session,

    route_result: dict,

    user_content: str,

    allow_sql: bool = True,

) -> dict:

    """

    Điều phối SQL Retrieval và RAG Retrieval.

    allow_sql:

        True  -> Cho phép truy vấn SQL.

        False -> Không truy vấn SQL.

    Chat đã đăng nhập:

        allow_sql = True

    Chat công khai:

        allow_sql = False

    """

    retrieval_modes = route_result.get(

        "retrieval_modes",

        [],

    )

    context = {

        "intent": route_result.get("intent"),

        "entity_type": route_result.get("entity_type"),

        "entity_name": route_result.get("entity_name"),

        "routing_source": route_result.get("source"),

        "target_route": None,

        "target_category": None,

        "expanded_query": user_content,

        "sql_data": None,

        "rag_data": [],

    }

    # ======================================

    # SQL RETRIEVAL

    # ======================================

    if "sql" in retrieval_modes and allow_sql:

        sql_result = retrieve_for_query(

            db=db,

            route_result=route_result,

        )

        context["sql_data"] = sql_result

    elif "sql" in retrieval_modes and not allow_sql:

        print("\n========== SQL RETRIEVAL SKIPPED ==========")

        print("Public chat không được truy vấn SQL.")

    # ======================================

    # RAG RETRIEVAL

    # ======================================

    if "rag" in retrieval_modes:

        (

            expanded_query,

            target_route,

            target_category,

        ) = build_expanded_rag_query(

            user_content=user_content,

            route_result=route_result,

        )

        context["expanded_query"] = expanded_query

        context["target_route"] = target_route

        context["target_category"] = target_category

        print("\n========== RAG QUERY EXPANSION ==========")

        print("Original query:", user_content)

        print("Expanded query:", expanded_query)


        print("Target category:", target_category)

        # ----------------------------------

        # RETRIEVE FROM QDRANT

        # ----------------------------------

        rag_results = retrieve_knowledge(

            query=expanded_query,

            top_k=RAG_TOP_K,

        )

        # ----------------------------------

        # RERANK RESULTS

        # ----------------------------------

        rag_results = rerank_rag_results(

            results=rag_results,

            target_route=None,

            target_category=target_category,

            intent=route_result.get("intent"),

        )

        # ----------------------------------

        # FILTER IRRELEVANT RESULTS

        # ----------------------------------

        rag_results = filter_relevant_rag_results(

            results=rag_results,

            intent=route_result.get("intent"),

            target_category=target_category,

        )

        context["rag_data"] = rag_results

        # ----------------------------------

        # DEBUG

        # ----------------------------------

        print("\n========== RAG RETRIEVAL DEBUG ==========")

        print("Retrieved results:", len(rag_results))

        for index, item in enumerate(rag_results, start=1):

            metadata = item.get("metadata") or {}

            print(f"\n--- RESULT {index} ---")

            print("Original Score:", item.get("score"))

            print("Rerank Score:", item.get("rerank_score"))

            print("Category:", metadata.get("category"))

            print("Tags:", metadata.get("tags"))

            print("Section:", metadata.get("section"))

            print("Feature:", metadata.get("feature_title"))

            print("Feature Number:", metadata.get("feature_number"))

            print("Route:", metadata.get("route"))

            print("Content:")

            print(item.get("content"))

    else:

        print("\n========== RAG SKIPPED ==========")

        print("Retrieval modes:", retrieval_modes)

    return context



# ==========================================

# 8. FORMAT ASSISTANT HISTORY

# ==========================================

def format_assistant_history(

    saved_response: dict,

) -> str:

    """

    Chuyển phản hồi assistant đã lưu thành văn bản.

    Hỗ trợ JSON cũ và JSON mới.

    """

    answer = saved_response.get("answer", "")

    if isinstance(answer, str):

        return answer

    if isinstance(answer, dict):

        history_parts = []

        for field in (

            "concept",

            "real_world_example",

            "code_example",

            "code_explanation",

            "practical_application",

        ):

            value = answer.get(field, "")

            if isinstance(value, str) and value.strip():

                history_parts.append(value.strip())

        return "\n".join(history_parts)

    return str(answer)



# ==========================================

# 11. SAVE ASSISTANT RESPONSE

# ==========================================

def save_assistant_response(

    db: Session,

    session_id: UUID | None,

    response_data: dict,

) -> dict:

    """

    Lưu câu trả lời AI nếu có session_id.

    session_id = UUID:

        Lưu vào ChatMessage.

    session_id = None:

        Không lưu, dùng cho public chat.

    """

    if session_id is None:

        return response_data

    ai_message = ChatMessage(

        session_id=session_id,

        role="assistant",

        content=json.dumps(

            response_data,

            ensure_ascii=False,

        ),

    )

    db.add(ai_message)

    db.commit()

    db.refresh(ai_message)

    return response_data



# ==========================================

# 14. PROCESS CHAT MESSAGE

# ==========================================

def process_chat_message(

    db: Session,

    session_id: UUID | None,

    user_content: str,

    allow_sql_retrieval: bool = True,

    custom_api_key: str | None = None,

) -> dict:

    """

    Facade for processing chat messages via ChatOrchestrator.

    Maintains backward compatibility with existing routers.

    """

    return orchestrator.process(

        db=db,

        session_id=session_id,

        user_content=user_content,

        allow_sql_retrieval=allow_sql_retrieval,

        custom_api_key=custom_api_key,

    )
