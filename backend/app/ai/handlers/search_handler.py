"""
Search Handler module for EduMentor AI.
Coordinates SQL retrieval (PostgreSQL), Qdrant semantic search, and RAG knowledge retrieval.
"""

from typing import Any
from sqlalchemy.orm import Session

from app.ai.query_router.config import (
    INTENT_CATEGORY_MAP,
    ROUTE_CATEGORY_MAP,
    ROUTE_KEYWORDS,
)
from app.ai.query_router.normalizer import normalize_text
from app.services.embedding_service import embedding_service
from app.services.qdrant_service import qdrant_course_service, qdrant_skill_service
from app.services.sql_retrieval import (
    course_to_dict,
    get_course_by_id,
    get_skill_by_id,
    retrieve_for_query,
    skill_to_dict,
)

RAG_TOP_K = 12


class SearchHandler:
    """
    Search Handler coordinates retrieval across PostgreSQL (exact/relational)
    and Qdrant (semantic vector search in edumentor_courses and edumentor_skills).
    """

    def detect_target_route(self, text: str) -> str | None:
        """Phát hiện route frontend từ từ khóa trong câu hỏi."""
        normalized = normalize_text(text)
        for route, keywords in ROUTE_KEYWORDS.items():
            for kw in keywords:
                if kw in normalized:
                    return route
        return None

    def build_expanded_rag_query(
        self,
        user_content: str,
        route_result: dict,
    ) -> tuple[str, str | None, str | None]:
        """Tạo expanded query để tăng độ chính xác của tìm kiếm ngữ nghĩa."""
        intent = route_result.get("intent")
        entity_name = route_result.get("entity_name")
        target_route = self.detect_target_route(user_content)
        target_category = None

        if target_route and target_route in ROUTE_CATEGORY_MAP:
            target_category = ROUTE_CATEGORY_MAP[target_route]
        elif intent in INTENT_CATEGORY_MAP:
            target_category = INTENT_CATEGORY_MAP[intent]

        expanded_parts = [user_content]
        if target_route:
            expanded_parts.append(f"Route: {target_route}")
        if target_category:
            expanded_parts.append(f"Category: {target_category}")
        if entity_name:
            expanded_parts.append(f"Entity: {entity_name}")

        expanded_query = " | ".join(expanded_parts)
        return expanded_query, target_route, target_category

    def search_courses_semantic(
        self,
        query: str,
        db: Session | None = None,
        allow_sql: bool = True,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        """
        Tìm kiếm khóa học theo ngữ nghĩa bằng Qdrant collection 'edumentor_courses'.
        Sử dụng ID để lấy dữ liệu chính thức từ PostgreSQL nếu có.
        """
        if not query or not query.strip():
            return []

        try:
            vector = embedding_service.encode_text(query.strip())
            hits = qdrant_course_service.search_courses(embedding=vector, limit=limit)
        except Exception as e:  # noqa: BLE001
            print(f"[SEARCH HANDLER] Qdrant course search failed: {e}")
            return []

        results = []
        for hit in hits:
            payload = hit.payload or {}
            course_id = payload.get("course_id")
            score = getattr(hit, "score", 0.0)

            # Try to fetch canonical record from PostgreSQL
            canonical_course = None
            if db is not None and allow_sql and course_id is not None:
                try:
                    c_record = get_course_by_id(db, int(course_id))
                    if c_record:
                        canonical_course = course_to_dict(c_record)
                except Exception as e:  # noqa: BLE001
                    print(f"[SEARCH HANDLER] PostgreSQL course lookup failed for ID {course_id}: {e}")

            if canonical_course:
                canonical_course["qdrant_score"] = score
                canonical_course["content"] = f"Khóa học: {canonical_course.get('title')} ({canonical_course.get('organization', 'N/A')})"
                canonical_course["score"] = score
                results.append(canonical_course)
            else:
                # Fallback to payload metadata from Qdrant
                results.append({
                    "course_id": course_id,
                    "title": payload.get("title", ""),
                    "level": payload.get("level", "N/A"),
                    "organization": payload.get("organization", "N/A"),
                    "instructor": payload.get("instructor", "N/A"),
                    "url": payload.get("url", ""),
                    "num_skills": payload.get("num_skills", 0),
                    "qdrant_score": score,
                    "content": f"Khóa học: {payload.get('title', '')} ({payload.get('organization', 'N/A')})",
                    "score": score,
                    "metadata": payload,
                })

        return results

    def search_skills_semantic(
        self,
        query: str,
        db: Session | None = None,
        allow_sql: bool = True,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        """
        Tìm kiếm kỹ năng theo ngữ nghĩa bằng Qdrant collection 'edumentor_skills'.
        Sử dụng ID để lấy dữ liệu chính thức từ PostgreSQL nếu có.
        """
        if not query or not query.strip():
            return []

        try:
            vector = embedding_service.encode_text(query.strip())
            hits = qdrant_skill_service.search_skill(embedding=vector, limit=limit)
        except Exception as e:  # noqa: BLE001
            print(f"[SEARCH HANDLER] Qdrant skill search failed: {e}")
            return []

        results = []
        for hit in hits:
            payload = hit.payload or {}
            skill_id = payload.get("skill_id")
            score = getattr(hit, "score", 0.0)

            canonical_skill = None
            if db is not None and allow_sql and skill_id is not None:
                try:
                    s_record = get_skill_by_id(db, int(skill_id))
                    if s_record:
                        canonical_skill = skill_to_dict(s_record)
                except Exception as e:  # noqa: BLE001
                    print(f"[SEARCH HANDLER] PostgreSQL skill lookup failed for ID {skill_id}: {e}")

            if canonical_skill:
                canonical_skill["qdrant_score"] = score
                canonical_skill["content"] = f"Kỹ năng: {canonical_skill.get('skill')}"
                canonical_skill["score"] = score
                results.append(canonical_skill)
            else:
                results.append({
                    "skill_id": skill_id,
                    "skill": payload.get("skill", ""),
                    "num_courses": payload.get("num_courses", 0),
                    "qdrant_score": score,
                    "content": f"Kỹ năng: {payload.get('skill', '')}",
                    "score": score,
                    "metadata": payload,
                })

        return results

    def build_retrieval_context(
        self,
        db: Session,
        route_result: dict,
        user_content: str,
        allow_sql: bool = True,
    ) -> dict[str, Any]:
        """
        Xây dựng ngữ cảnh truy xuất đầy đủ gồm SQL data và Qdrant semantic data.
        Đồng bộ retrieval_strategy và retrieval_modes.
        """
        retrieval_modes = route_result.get("retrieval_modes", [])
        retrieval_strategy = route_result.get("retrieval_strategy", "")
        task_type = route_result.get("task_type", "")
        intent = route_result.get("intent", "")

        context: dict[str, Any] = {
            "intent": intent,
            "task_type": task_type,
            "retrieval_strategy": retrieval_strategy,
            "entity_type": route_result.get("entity_type"),
            "entity_name": route_result.get("entity_name"),
            "routing_source": route_result.get("source"),
            "target_route": None,
            "target_category": None,
            "expanded_query": user_content,
            "sql_data": None,
            "qdrant_data": [],
            "rag_data": [],
        }

        needs_sql = "sql" in retrieval_modes or "sql" in retrieval_strategy
        needs_qdrant = (
            "qdrant" in retrieval_modes
            or "qdrant" in retrieval_strategy
            or "rag" in retrieval_modes
            or task_type in ("course_semantic_search", "skill_semantic_search", "hybrid_search")
        )

        # 1. SQL Retrieval (PostgreSQL)
        if needs_sql and allow_sql:
            try:
                sql_result = retrieve_for_query(
                    db=db,
                    route_result=route_result,
                )
                context["sql_data"] = sql_result
            except Exception as e:  # noqa: BLE001
                print(f"[SEARCH HANDLER] SQL retrieval error: {e}")
                context["sql_data"] = {"found": False, "error": str(e)}
        elif needs_sql and not allow_sql:
            print("[SEARCH HANDLER] Public chat: SQL retrieval skipped.")

        # 2. Qdrant Semantic Retrieval
        # Execute if strategy specifies qdrant OR if SQL search found no exact match for course/skill search
        sql_found = bool(context["sql_data"] and context["sql_data"].get("found"))
        should_run_qdrant = needs_qdrant or (
            task_type in ("course_name_search", "skill_name_search") and not sql_found
        )

        if should_run_qdrant:
            search_query = route_result.get("entity_name") or user_content
            qdrant_results: list[dict[str, Any]] = []

            is_skill_search = task_type in ("skill_name_search", "skill_semantic_search") or (
                intent == "skill_search"
            )
            is_course_search = task_type in ("course_name_search", "course_semantic_search") or (
                intent in ("course_search", "course_question")
            )

            if is_skill_search:
                qdrant_results = self.search_skills_semantic(
                    query=search_query,
                    db=db,
                    allow_sql=allow_sql,
                    limit=5,
                )
            elif is_course_search:
                qdrant_results = self.search_courses_semantic(
                    query=search_query,
                    db=db,
                    allow_sql=allow_sql,
                    limit=5,
                )
            else:
                # General semantic / learning path / other: query both collections
                course_hits = self.search_courses_semantic(
                    query=search_query,
                    db=db,
                    allow_sql=allow_sql,
                    limit=3,
                )
                skill_hits = self.search_skills_semantic(
                    query=search_query,
                    db=db,
                    allow_sql=allow_sql,
                    limit=3,
                )
                qdrant_results = course_hits + skill_hits

            context["qdrant_data"] = qdrant_results
            context["rag_data"] = qdrant_results

        return context

    def handle(
        self,
        db: Session,
        route_result: dict,
        user_content: str,
        allow_sql: bool = True,
    ) -> dict[str, Any]:
        """
        Thực thi tìm kiếm và đóng gói kết quả tìm kiếm thống nhất.
        """
        context = self.build_retrieval_context(
            db=db,
            route_result=route_result,
            user_content=user_content,
            allow_sql=allow_sql,
        )

        sql_data = context.get("sql_data") or {}
        qdrant_data = context.get("qdrant_data") or []
        sql_found = bool(sql_data.get("found", False) if isinstance(sql_data, dict) else False)
        qdrant_found = len(qdrant_data) > 0

        return {
            "search_type": route_result.get("task_type", "search"),
            "retrieval_context": context,
            "sql_data": sql_data,
            "qdrant_data": qdrant_data,
            "rag_data": qdrant_data,
            "found": sql_found or qdrant_found,
        }


search_handler = SearchHandler()
