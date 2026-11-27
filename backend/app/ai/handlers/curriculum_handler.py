"""
Curriculum & Syllabus Handler for EduMentor AI Chatbot.
Handles:
Course Web Search (Curriculum): Verifies course existence in EduMentor DB first,
then enriches granular syllabus via Tavily Web Search.
"""

import json
import logging
from typing import Any

from sqlalchemy.orm import Session

from app.ai.client import generate_text
from app.services import sql_retrieval
from app.services.tavily_service import tavily_service

logger = logging.getLogger("curriculum_handler")


# =====================================================================
# SYSTEM PROMPT (EMBEDDED DIRECTLY IN HANDLER)
# =====================================================================

COURSE_CURRICULUM_SYSTEM_PROMPT = """BẠN LÀ CHUYÊN GIA TỔNG HỢP GIÁO TRÌNH VÀ CHI TIẾT KHÓA HỌC CỦA EDUMENTOR AI.

NHIỆM VỤ CỦA BẠN:
Cung cấp thông tin chi tiết đầy đủ, giáo trình, thời gian hoàn thành và nội dung chi tiết các module/tuần học của khóa học trong hệ thống EduMentor bằng cách kết hợp thông tin CSDL EduMentor và kết quả tìm kiếm chi tiết từ Web.

QUY TẮC BẮT BUỘC (STRICT CONSTRAINTS):
1. NGUỒN DỮ LIỆU CHÍNH XÁC:
   - Thông tin cơ bản: Tên khóa học, tổ chức, giảng viên, cấp độ, tổng quan modules (`modules_summary`), thời gian hoàn thành (`duration_schedule`): Lấy từ EDUMENTOR_DATABASE_DATA.
   - BẮT BUỘC nêu rõ thời gian hoàn thành (ví dụ từ trường `duration_schedule`: khoảng X giờ / Y tuần hoặc thời lượng tương đương) và số lượng modules.
   - Nội dung chi tiết các bài học, tuần học, chủ đề từng module: Lấy từ mục `description` trong EDUMENTOR_DATABASE_DATA và TAVILY_WEB_RESULTS.
   - TUYỆT ĐỐI không bịa ra nội dung module hoặc bài giảng không có cơ sở.

2. CẤU TRÚC PHẢN HỒI (BẮT BUỘC ĐẦY ĐỦ CÁC MỤC SAU):
   - **Tổng quan khóa học:**
     * Tên khóa học: ...
     * Đơn vị đào tạo / Giảng viên: ...
     * Cấp độ & Đánh giá: ...
     * Thời gian hoàn thành dự kiến: (Lấy từ `duration_schedule` trong CSDL)
     * Số lượng module: (Lấy từ `modules_summary` hoặc số module đếm được trong `description`)
   - **Chi tiết giáo trình / Cấu trúc các Module (Syllabus Breakdown):**
     * Module 1: Tên chủ đề & tóm tắt các bài học / thời lượng.
     * Module 2: ...
     * Module 3: ...
     * (Liệt kê đầy đủ và có thứ tự tất cả các module có trong mục `description` của CSDL và kết quả web).
   - **Kỹ năng đạt được & Mục tiêu đầu ra:** Học viên sẽ làm được gì sau khi học hết khóa học này.
   - **Link tham gia khóa học:** Dẫn link URL của khóa học từ CSDL (`url`).

3. ĐỊNH DẠNG JSON ĐẦU RA:
   Chỉ trả về DUY NHẤT một chuỗi JSON hợp lệ với cấu trúc sau, không kèm bất kỳ giải thích nào bên ngoài:
   {
     "answer": "Nội dung chi tiết khóa học định dạng Markdown chuẩn, rõ ràng, đẹp mắt...",
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

class CourseCurriculumAdvisor:
    """
    Business logic for retrieving course syllabus and curriculum:
    1. Verifies that the course exists in the EduMentor database.
    2. If found, checks DB metadata (e.g. `modules` summary).
    3. Calls Tavily Search to fetch granular weekly syllabus / lesson breakdown.
    4. Synthesizes a structured curriculum guide.
    """

    def handle(
        self,
        db: Session,
        course_name: str | None,
        user_query: str,
        organization: str | None = None,
        conversation_history: str = "",
        custom_api_key: str | None = None,
    ) -> str | dict[str, Any]:
        """
        Tìm và tổng hợp giáo trình khóa học.
        """
        # 1. BẮT BUỘC KIỂM TRA TRONG CSDL EDUMENTOR
        matched_course = None
        if course_name and str(course_name).strip():
            c = sql_retrieval.find_course(db, course_name.strip())
            if c:
                matched_course = sql_retrieval.course_to_dict(c) if hasattr(c, "course_id") else c
            if not matched_course:
                # Tìm kiếm tương đối qua SQL
                candidates = sql_retrieval.search_courses(db, course_name.strip(), limit=1)
                if candidates:
                    matched_course = candidates[0]

        # Fallback 1b: Quét qua conversation_history nếu chưa tìm thấy khóa học
        if not matched_course and conversation_history:
            import re
            bold_matches = re.findall(r"\*\*([^*]+)\*\*", conversation_history)
            for cand in reversed(bold_matches):
                cand_clean = cand.strip()
                if len(cand_clean) > 3 and not any(
                    kw in cand_clean.lower()
                    for kw in ["luu y", "chu y", "tong quan", "goi y", "de xuat", "module", "tuan", "rating", "danh gia", "thong tin"]
                ):
                    c = sql_retrieval.find_course(db, cand_clean)
                    if c:
                        matched_course = sql_retrieval.course_to_dict(c) if hasattr(c, "course_id") else c
                    if not matched_course:
                        cands = sql_retrieval.search_courses(db, cand_clean, limit=1)
                        if cands:
                            matched_course = cands[0]
                    if matched_course:
                        break

        # 2. NẾU KHÔNG TÌM THẤY TRONG CSDL EDUMENTOR:
        # Tuyệt đối KHÔNG gọi Tavily tìm khóa học bên ngoài!
        if not matched_course:
            return {
                "answer": (
                    f"Rất tiếc, hệ thống EduMentor hiện tại không tìm thấy khóa học nào có tên "
                    f"**\"{course_name or user_query}\"** trong cơ sở dữ liệu.\n\n"
                    "EduMentor chỉ hỗ trợ xem giáo trình và bài học chi tiết cho các khóa học đã được kiểm định "
                    "trong hệ thống. Bạn có thể:\n"
                    "1. Tra cứu các khóa học khác hiện có trên thanh tìm kiếm của EduMentor.\n"
                    "2. Sử dụng công cụ [AI Lộ trình](http://localhost:5173/ai-learning-path) để tạo một lộ trình "
                    "học tập cá nhân hóa phù hợp với mục tiêu của bạn."
                ),
                "suggestions": [
                    {"label": "Tạo lộ trình AI", "prompt": "Hướng dẫn tôi tạo lộ trình trên trang AI Lộ trình"},
                    {"label": "Tìm khóa học", "prompt": "Tìm các khóa học phổ biến trong hệ thống EduMentor"},
                ],
            }

        # 3. KHI TÌM THẤY TRONG CSDL EDUMENTOR:
        # Lấy thông tin sẵn có trong CSDL (bao gồm trường `modules` và `schedule`)
        course_title = matched_course.get("title", "")
        course_org = matched_course.get("organization") or organization or ""
        course_instructor = matched_course.get("instructor") or "N/A"
        course_modules = matched_course.get("modules") or "Theo cấu trúc bài học trong mô tả"
        course_schedule = matched_course.get("schedule") or "Tùy thuộc vào tốc độ người học"
        course_level = matched_course.get("level") or "N/A"
        course_rating = matched_course.get("rating") or "N/A"
        course_desc = matched_course.get("description") or ""
        course_url = matched_course.get("url") or ""

        db_course_data = {
            "title": course_title,
            "organization": course_org,
            "instructor": course_instructor,
            "level": course_level,
            "rating": course_rating,
            "modules_summary": course_modules,
            "duration_schedule": course_schedule,
            "description": course_desc[:3000],
            "url": course_url,
        }

        # 4. GỌI TAVILY ĐỂ LẤY CHI TIẾT GIÁO TRÌNH / BÀI HỌC CỤ THỂ TỪ WEB
        tavily_data = []
        if tavily_service.is_configured:
            tavily_res = tavily_service.search_course_curriculum(
                course_title=course_title,
                organization=course_org if course_org != "N/A" else None,
                max_results=3,
            )
            if tavily_res.get("success"):
                tavily_data = tavily_res.get("results") or []

        # 5. Xây dựng Prompt tổng hợp
        prompt = f"""
{COURSE_CURRICULUM_SYSTEM_PROMPT}

==================================================
EDUMENTOR DATABASE DATA (VERIFIED OFFICIAL)
==================================================
{json.dumps(db_course_data, ensure_ascii=False, indent=2)}

==================================================
TAVILY WEB SEARCH RESULTS (SYLLABUS & LESSONS)
==================================================
{json.dumps(tavily_data, ensure_ascii=False, indent=2)}

==================================================
USER QUESTION
==================================================
{user_query}

==================================================
CONVERSATION HISTORY
==================================================
{conversation_history}

==================================================
INSTRUCTION
==================================================
1. Trình bày tổng quan khóa học: Tên, Đơn vị đào tạo ({course_org}), Giảng viên ({course_instructor}), Cấp độ ({course_level}), Thời gian hoàn thành dự kiến ({course_schedule}), Tổng số module: BẮT BUỘC nêu rõ thời gian hoàn thành và số lượng module từ CSDL ({course_modules}), TUYỆT ĐỐI KHÔNG nói hệ thống không lưu trữ hoặc phỏng đoán khác.
2. Cung cấp chi tiết giáo trình/lộ trình từng module và bài học từ CSDL (đặc biệt là mục description) và kết quả tìm kiếm web. Liệt kê rõ ràng và chi tiết theo từng module (Module 1, Module 2, Module 3...).
3. Nêu rõ kỹ năng đầu ra đạt được sau khi học xong.
4. Trả về đúng định dạng JSON có 'answer' (Markdown) và 'suggestions'.
"""
        return generate_text(prompt, api_key=custom_api_key)


course_curriculum_advisor = CourseCurriculumAdvisor()
curriculum_handler = course_curriculum_advisor
