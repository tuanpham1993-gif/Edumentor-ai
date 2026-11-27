"""
Recommendation Handler for EduMentor AI Chatbot.
Handles:
Course Recommendation: Analyzes learner goals/level and evaluates/ranks
candidate courses retrieved strictly from EduMentor database.
"""

import json
import logging
from typing import Any

from sqlalchemy.orm import Session

from app.ai.client import generate_text
from app.services import sql_retrieval
from app.services.qdrant_service import qdrant_course_service

# Re-export for backward compatibility
from app.ai.handlers.curriculum_handler import (
    CourseCurriculumAdvisor,
    course_curriculum_advisor,
)

logger = logging.getLogger("recommendation_handler")


# =====================================================================
# SYSTEM PROMPT (EMBEDDED DIRECTLY IN HANDLER)
# =====================================================================

COURSE_RECOMMENDATION_SYSTEM_PROMPT = """BẠN LÀ CHUYÊN GIA TƯ VẤN KHÓA HỌC VÀ LỘ TRÌNH CỦA EDUMENTOR AI.

NHIỆM VỤ CỦA BẠN:
Phân tích trình độ, mục tiêu học tập của người học và đánh giá, xếp hạng các khóa học phù hợp nhất TỪ DANH SÁCH KHÓA HỌC CÓ TRONG HỆ THỐNG EDUMENTOR ĐƯỢC CUNG CẤP.

QUY TẮC BẮT BUỘC (STRICT CONSTRAINTS):
1. CHỈ SỬ DỤNG DỮ LIỆU KHÓA HỌC THẬT TRONG CANDIDATE_COURSES ĐƯỢC TRUYỀN VÀO:
   - TUYỆT ĐỐI KHÔNG tự bịa ra khóa học không tồn tại trong danh sách.
   - Nếu danh sách CANDIDATE_COURSES rỗng hoặc không có khóa phù hợp, hãy thông báo lịch sự rằng hiện tại EduMentor chưa có khóa học khớp hoàn toàn, và hướng dẫn người học tạo lộ trình cá nhân hóa tại AI Lộ trình: http://localhost:5173/ai-learning-path.

2. CẤU TRÚC PHÂN TÍCH VÀ XẾP HẠNG (COURSE RANKING):
   - **Phân tích nhu cầu:** Xác định rõ mục tiêu nghề nghiệp, trình độ hiện tại (Beginner / Intermediate / Advanced) và kỹ năng mong muốn.
   - **Lộ trình đề xuất theo thứ tự ưu tiên:**
     * Khóa 1 (Nền tảng / Bắt đầu): Khóa học cơ bản, giúp nắm vững tư duy và cú pháp/khái niệm cốt lõi.
     * Khóa 2 (Thực hành / Phát triển): Khóa học áp dụng kỹ năng vào dự án thực tế, xây dựng sản phẩm.
     * Khóa 3 (Nâng cao / Chuyên sâu): Khóa học tối ưu hóa, kiến trúc nâng cao hoặc chuyên đề đặc thù.
   - **Với mỗi khóa học được đề cử, bắt buộc nêu:**
     * Tên chính xác của khóa học (in đậm).
     * Tổ chức / Giảng viên & Đánh giá (Rating).
     * Cấp độ (Level) & Số lượng module.
     * Lý do vì sao khóa học này phù hợp với trình độ và mục tiêu của học viên.
     * Kỹ năng đạt được sau khi hoàn thành.
     * Link khóa học nếu có trong dữ liệu (sử dụng link URL từ database).

3. ĐỊNH DẠNG ĐƯỜNG DẪN (LINK URL):
   - Chỉ được dẫn URL khóa học có sẵn trong dữ liệu hoặc đường dẫn nội bộ:
     * AI Lộ trình: http://localhost:5173/ai-learning-path
   - TUYỆT ĐỐI không bịa link URL bên ngoài.

4. BẮT BUỘC ĐỊNH DẠNG JSON ĐẦU RA:
   Chỉ trả về DUY NHẤT một chuỗi JSON hợp lệ với cấu trúc sau, không kèm bất kỳ giải thích nào bên ngoài:
   {
     "answer": "Nội dung phân tích và gợi ý khóa học định dạng Markdown chuẩn, rõ ràng, đẹp mắt...",
     "suggestions": [
       {"label": "...", "prompt": "..."},
       {"label": "...", "prompt": "..."},
       {"label": "...", "prompt": "..."}
     ]
   }
"""


# =====================================================================
# HANDLER
# =====================================================================

class RecommendationHandler:
    """
    Handler for recommending courses based on learner's profile,
    ranking candidate courses retrieved strictly from EduMentor database.
    """

    def handle(
        self,
        db: Session,
        user_query: str,
        route_result: dict[str, Any],
        conversation_history: str = "",
        custom_api_key: str | None = None,
    ) -> str:
        """
        Gợi ý và xếp hạng khóa học phù hợp với người học.
        """
        entity_name = route_result.get("entity_name") or ""
        level = route_result.get("level")
        target_role = route_result.get("target_role")
        known_skill = route_result.get("known_skill")

        # 1. Thu thập Candidate Courses từ PostgreSQL (bảng `courses`)
        candidate_courses_map: dict[int, dict[str, Any]] = {}

        # 1.1 Tìm kiếm theo thực thể chính hoặc vai trò/kỹ năng
        search_terms = [t for t in [entity_name, target_role, known_skill] if t and len(str(t).strip()) > 1]
        if not search_terms:
            search_terms = [user_query]

        for term in search_terms:
            db_courses = sql_retrieval.search_courses(db, query=term, limit=6)
            for c in db_courses:
                cid = c.get("course_id")
                if cid and cid not in candidate_courses_map:
                    candidate_courses_map[cid] = c

        # 1.2 Tìm kiếm mở rộng qua Qdrant Vector Search nếu số lượng ứng viên < 5
        if len(candidate_courses_map) < 5:
            try:
                vector_results = qdrant_course_service.search_courses(user_query, limit=5)
                for hit in vector_results:
                    cid = hit.get("course_id")
                    if cid and cid not in candidate_courses_map:
                        candidate_courses_map[cid] = {
                            "course_id": cid,
                            "title": hit.get("title", ""),
                            "level": hit.get("level", "N/A"),
                            "organization": hit.get("organization", "N/A"),
                            "rating": hit.get("rating"),
                            "instructor": hit.get("instructor", "N/A"),
                            "url": hit.get("url", ""),
                            "description": hit.get("description", ""),
                        }
            except Exception as q_err:
                logger.warning(f"Qdrant vector search during recommendation failed: {q_err}")

        # Chuẩn bị dữ liệu danh sách ứng viên sạch gọn cho LLM
        candidate_list = []
        for c in list(candidate_courses_map.values())[:8]:
            desc = c.get("description") or ""
            candidate_list.append(
                {
                    "course_id": c.get("course_id"),
                    "title": c.get("title"),
                    "level": c.get("level", "N/A"),
                    "organization": c.get("organization", "N/A"),
                    "instructor": c.get("instructor", "N/A"),
                    "rating": c.get("rating"),
                    "modules": c.get("modules", "N/A"),
                    "skills": c.get("skills") or [],
                    "url": c.get("url", ""),
                    "description": desc[:300] + ("..." if len(desc) > 300 else ""),
                }
            )

        # 2. Xây dựng Prompt cho Gemini
        learner_profile = {
            "query": user_query,
            "target_role": target_role or "N/A",
            "current_level": level or "Beginner",
            "known_skill": known_skill or "N/A",
        }

        prompt = f"""
{COURSE_RECOMMENDATION_SYSTEM_PROMPT}

==================================================
LEARNER PROFILE & GOALS
==================================================
{json.dumps(learner_profile, ensure_ascii=False, indent=2)}

==================================================
CANDIDATE COURSES (FROM EDUMENTOR DATABASE ONLY)
==================================================
{json.dumps(candidate_list, ensure_ascii=False, indent=2)}

==================================================
CONVERSATION HISTORY
==================================================
{conversation_history}

==================================================
INSTRUCTION
==================================================
1. Đánh giá nhu cầu học tập của người học dựa trên query và profile.
2. Chọn và xếp hạng từ danh sách CANDIDATE COURSES các khóa học tốt nhất (từ nền tảng -> thực hành -> nâng cao).
3. Nêu rõ lý do tại sao khóa học phù hợp với người học.
4. Trả về đúng định dạng JSON có 'answer' (Markdown) và 'suggestions'.
"""
        return generate_text(prompt, api_key=custom_api_key)


recommendation_handler = RecommendationHandler()
