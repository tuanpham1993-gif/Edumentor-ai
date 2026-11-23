"""
Knowledge Handler module for EduMentor AI.
Handles conceptual knowledge, skill explanations, course info,
system operations, and learning path guidance using Gemini.
"""

import json
import re

from app.ai.client import generate_text
from app.ai.prompts.tutor import TUTOR_SYSTEM_PROMPT


def build_learning_path_instructions() -> str:
    """Hướng dẫn Gemini trả lời các câu hỏi về Learning Path."""
    return """
LEARNING PATH MODE

Người học đang hỏi về AI Learning Path Advisor và Roadmap Canvas của EduMentor.

Quy tắc bắt buộc:
1. Sử dụng các kết quả RAG có category = learning_path làm nguồn chính.
2. Phân biệt các thao tác:
   - Tạo lộ trình mới.
   - Xem bản nháp Draft Roadmap Canvas.
   - Điều chỉnh lộ trình bằng hội thoại.
   - Lưu lộ trình bằng Save This Path.
   - Bỏ bản nháp bằng Discard.
   - Xem và chỉnh sửa lộ trình đã lưu.
3. Người học bắt đầu tại trang /ai-learning-path, chọn + Create New Path with AI.
4. Trả lời bằng ngôn ngữ người học sử dụng.
5. Giữ nguyên cấu trúc JSON của SYSTEM PROMPT.
6. LIÊN KẾT & HƯỚNG DẪN SANG TÍNH NĂNG AI LỘ TRÌNH:
   - Trong answer, giới thiệu và nhắc người học truy cập:
     `http://localhost:5173/ai-learning-path` (hoặc tab "Lộ trình" trên Navbar).
   - Hướng dẫn người học bấm "+ Tạo lộ trình mới với AI" (+ Create New Path with AI).
7. BẮT BUỘC GỢI Ý (SUGGESTIONS) CHUYỂN SANG AI LỘ TRÌNH:
   Trong suggestions, có ít nhất 1 gợi ý kết nối với AI Lộ trình:
   {
     "label": "Tạo lộ trình AI",
     "prompt": "Hướng dẫn tôi cách tạo lộ trình mới trên trang AI Lộ trình của EduMentor"
   }
"""


def build_system_operation_instructions() -> str:
    """Hướng dẫn Gemini xử lý các yêu cầu thao tác hệ thống từng bước."""
    return """
SYSTEM OPERATION - STEP BY STEP MODE

Người học đang yêu cầu hướng dẫn thực hiện thao tác trên EduMentor.

Quy tắc bắt buộc:
1. Dùng RAG_DATA làm nguồn chính.
2. Hướng dẫn theo thứ tự từng bước, ngắn gọn và dễ làm theo.
3. Nếu người học nói đã truy cập trang, không lặp lại đường dẫn như câu trả lời chính.
4. Chỉ nêu tên nút, trường nhập liệu nếu được tài liệu RAG_DATA xác nhận.
5. Không tự bịa form fields, nút bấm, thông báo thành công.
6. Không yêu cầu người học gửi mật khẩu hoặc thông tin đăng nhập.
"""


def build_system_operation_response(retrieval_context: dict) -> dict | None:
    """Trả lời trực tiếp yêu cầu lấy đường dẫn hợp lệ hoặc từ chối link không chắc chắn."""
    target_route = retrieval_context.get("target_route")

    allowed_links = {
        "/login": ("Đăng nhập", "http://localhost:5173/login"),
        "/register": ("Đăng ký", "http://localhost:5173/register"),
        "/ai-learning-path": ("AI Lộ trình", "http://localhost:5173/ai-learning-path"),
    }

    if target_route in allowed_links:
        title, url = allowed_links[target_route]
        return {
            "answer": f"Bạn có thể truy cập trang **{title}** của EduMentor tại đường dẫn sau:\n{url}",
            "suggestions": [],
        }

    # Nếu hỏi direct_link của bất kỳ trang nào khác hoặc không có route cụ thể:
    # Tuyệt đối không gọi AI gen link, mà từ chối lịch sự và hướng dẫn qua Navbar
    return {
        "answer": (
            "Xin lỗi bạn, hiện tại mình không thể cung cấp đường dẫn trực tiếp cho trang này. "
            "Bạn vui lòng nhìn lên thanh menu điều hướng (Navbar) ở phía trên màn hình và bấm vào mục tương ứng để truy cập nhé!"
        ),
        "suggestions": [
            {"label": "AI Lộ trình", "prompt": "Hướng dẫn tôi tạo lộ trình trên trang AI Lộ trình"}
        ],
    }




class KnowledgeHandler:
    """
    Knowledge Handler answers educational and system questions using Gemini,
    incorporating relational context and documentation.
    """

    def handle(
        self,
        route_result: dict,
        retrieval_context: dict,
        conversation_history: str,
        custom_api_key: str | None = None,
    ) -> str | dict:
        """
        Xử lý câu hỏi kiến thức bằng Gemini hoặc trả lời trực tiếp cho direct link.
        Trả về chuỗi JSON raw từ LLM hoặc dict trực tiếp.
        """
        # Kiểm tra direct link cho system_operation
        if route_result.get("intent") == "system_operation" and route_result.get("operation_type") == "direct_link":
            direct_resp = build_system_operation_response(retrieval_context)
            if direct_resp is not None:
                return direct_resp

        context_json = json.dumps(
            retrieval_context,
            ensure_ascii=False,
            indent=2,
            default=str,
        )

        prompt = f"""
{TUTOR_SYSTEM_PROMPT}

==================================================
CONVERSATION HISTORY
==================================================

{conversation_history}

==================================================
QUERY ROUTER RESULT
==================================================

{json.dumps(route_result, ensure_ascii=False, indent=2)}

==================================================
RETRIEVED KNOWLEDGE
==================================================

{context_json}

==================================================
INSTRUCTIONS
==================================================

1. Trả lời câu hỏi mới nhất của người học.
2. Sử dụng lịch sử hội thoại để hiểu ngữ cảnh.
3. PHẠM VI HỖ TRỢ:
   - Chỉ hỗ trợ các câu hỏi liên quan đến HỌC TẬP, LẬP TRÌNH, KHÓA HỌC, KỸ NĂNG, VÀ HƯỚNG DẪN EDUMENTOR.
   - Nếu người học hỏi về người, đồ vật hoặc chủ đề ngoài phạm vi học tập, hãy từ chối một cách lịch sự, nhã nhặn.
4. NGUYÊN TẮC ĐƯỜNG DẪN (LINK URL):
   - CHỈ ĐƯỢC PHÉP trả về tối đa 3 link này:
     * Đăng nhập: http://localhost:5173/login
     * Đăng ký: http://localhost:5173/register
     * AI Lộ trình: http://localhost:5173/ai-learning-path
   - TUYỆT ĐỐI KHÔNG BỊA LINK KHÁC (như link trang Ôn tập, Đánh giá, Khóa học của tôi,...).
   - Nếu người học hỏi về trang Ôn tập, Đánh giá hoặc các trang khác, hãy xin lỗi lịch sự vì không có link trực tiếp và hướng dẫn người học nhìn lên thanh Navbar phía trên để bấm vào mục tương ứng.
5. Nếu có SQL_DATA:
   - Sử dụng dữ liệu này khi trả lời câu hỏi về Course và Skill.
   - Không tự tạo Course hoặc Skill không tồn tại trong dữ liệu.
   - Nếu found = false, thông báo rằng hệ thống không tìm thấy dữ liệu phù hợp.
6. Nếu có RAG_DATA:
   - Ưu tiên nội dung tài liệu được truy xuất.
7. Nếu không có SQL_DATA và RAG_DATA:
   - Trả lời bằng kiến thức lập trình / khoa học máy tính tổng quát của Gemini.
8. Trả lời bằng cùng ngôn ngữ người học sử dụng.
9. Tuân thủ chính xác cấu trúc JSON trong SYSTEM PROMPT:
   {{"answer": "...", "suggestions": [{{"label": "...", "prompt": "..."}}]}}
"""

        intent = route_result.get("intent")
        operation_type = route_result.get("operation_type")

        if intent == "learning_path_request":
            prompt += build_learning_path_instructions()
        elif intent == "system_operation" and operation_type == "step_by_step":
            prompt += build_system_operation_instructions()

        ai_text = generate_text(prompt, api_key=custom_api_key)
        return ai_text


knowledge_handler = KnowledgeHandler()
