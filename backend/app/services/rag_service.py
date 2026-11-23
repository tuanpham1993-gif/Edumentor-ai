"""
RAG Service using Qdrant vector collections (edumentor_courses, edumentor_skills).
Provides retrieve_knowledge interface performing actual semantic search.
"""

from typing import Any

DEFAULT_TOP_K = 5


def retrieve_knowledge(
    query: str,
    top_k: int = DEFAULT_TOP_K,
) -> list[dict[str, Any]]:
    """
    Truy xuất tri thức ngữ nghĩa thực tế qua Qdrant và EmbeddingService.
    Tìm kiếm song song các khóa học và kỹ năng phù hợp nhất.
    """
    if not isinstance(query, str) or not query.strip():
        raise ValueError("Query cannot be empty.")

    if not isinstance(top_k, int) or isinstance(top_k, bool) or top_k < 1:
        raise ValueError("top_k must be a positive integer.")

    try:
        from app.services.embedding_service import embedding_service
        from app.services.qdrant_service import qdrant_course_service, qdrant_skill_service

        vector = embedding_service.encode_text(query.strip())
        results: list[dict[str, Any]] = []

        # 1. Search Courses
        try:
            course_hits = qdrant_course_service.search_courses(embedding=vector, limit=top_k)
            for h in course_hits:
                payload = h.payload or {}
                results.append({
                    "content": f"Khóa học: {payload.get('title', '')} - Tổ chức: {payload.get('organization', 'N/A')}",
                    "score": getattr(h, "score", 0.0),
                    "metadata": payload,
                })
        except Exception as e:  # noqa: BLE001
            print(f"[RAG SERVICE] Qdrant course retrieval error: {e}")

        # 2. Search Skills
        try:
            skill_hits = qdrant_skill_service.search_skill(embedding=vector, limit=top_k)
            for h in skill_hits:
                payload = h.payload or {}
                results.append({
                    "content": f"Kỹ năng: {payload.get('skill', '')}",
                    "score": getattr(h, "score", 0.0),
                    "metadata": payload,
                })
        except Exception as e:  # noqa: BLE001
            print(f"[RAG SERVICE] Qdrant skill retrieval error: {e}")

        # Sort combined results by score descending and take top_k
        results.sort(key=lambda x: x.get("score", 0.0), reverse=True)
        return results[:top_k]

    except Exception as e:  # noqa: BLE001
        print(f"[RAG SERVICE] Semantic retrieval fallback: {e}")
        return []
