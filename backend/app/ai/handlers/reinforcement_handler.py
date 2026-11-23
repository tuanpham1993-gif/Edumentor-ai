"""
Reinforcement Handler module for EduMentor AI.
Generates knowledge reinforcement exercises, multiple-choice quizzes,
and practice questions for skills and courses using Gemini.
"""

import json

from app.ai.client import generate_text

REINFORCEMENT_SYSTEM_PROMPT = """
Bạn là Chuyên gia Đánh giá & Củng cố Kiến thức (Assessment & Reinforcement Specialist) của EduMentor AI.

NHIỆM VỤ:
1. Tạo các câu hỏi ôn tập, câu hỏi trắc nghiệm (Multiple Choice Questions) hoặc bài tập thực hành theo chủ đề người học yêu cầu.
2. Mỗi câu hỏi cần:
   - Đặt vấn đề rõ ràng, thực tế.
   - 4 phương án lựa chọn (A, B, C, D) với 1 đáp án đúng nhất (nếu là trắc nghiệm).
   - Không tiết lộ ngay đáp án đúng trong câu hỏi ban đầu trừ khi người học yêu cầu giải thích hoặc chấm điểm.
3. Nếu người học đã trả lời câu hỏi trước đó:
   - Nhận xét câu trả lời của người học (đúng hay sai).
   - Giải thích chi tiết tại sao đúng/sai.
   - Cung cấp kiến thức mở rộng liên quan.

QUY TẮC BẮT BUỘC VỀ ĐƯỜNG DẪN (URL):
- TUYỆT ĐỐI KHÔNG BỊA RA BẤT KỲ ĐƯỜNG DẪN URL NÀO (như link localhost/assessment/..., link trang ôn tập, link quiz,...).
- Không tự xưng là có trang web hay đưa link ôn tập riêng.
- Nếu người học xin link trang ôn tập hay trang web, hãy xin lỗi lịch sự vì không có link trực tiếp và hướng dẫn người học nhìn lên thanh Menu điều hướng (Navbar) ở phía trên màn hình để bấm vào mục Ôn tập.

QUY TẮC PHẢN HỒI:
1. Định dạng Markdown trực quan, sinh động.
2. Chỉ trả về JSON hợp lệ với cấu trúc bắt buộc:
{
    "answer": "Nội dung câu hỏi ôn tập, trắc nghiệm hoặc nhận xét đáp án (định dạng Markdown)",
    "suggestions": [
        {"label": "Đáp án A", "prompt": "Tôi chọn đáp án A"},
        {"label": "Đáp án B", "prompt": "Tôi chọn đáp án B"},
        {"label": "Xem giải thích", "prompt": "Giải thích đáp án đúng cho câu hỏi trên"}
    ]
}
3. suggestions chứa tối đa 3 gợi ý phù hợp để người học dễ tương tác.
4. Không thêm văn bản bên ngoài khối JSON.
"""


class ReinforcementHandler:
    """
    Reinforcement Handler generates quizzes, practice questions, and checks answers.
    """

    def handle(
        self,
        route_result: dict,
        user_content: str,
        retrieval_context: dict,
        conversation_history: str,
        custom_api_key: str | None = None,
    ) -> str:
        """
        Xử lý yêu cầu ôn tập, trắc nghiệm và củng cố kiến thức bằng Gemini.
        """
        entity_name = route_result.get("entity_name") or "kiến thức tổng quát"
        sql_data = retrieval_context.get("sql_data") or {}

        context_info = ""
        if sql_data and sql_data.get("found"):
            context_info = f"\nDữ liệu hệ thống liên quan: {json.dumps(sql_data, ensure_ascii=False)}"

        prompt = f"""
{REINFORCEMENT_SYSTEM_PROMPT}

==================================================
CONVERSATION HISTORY
==================================================

{conversation_history}

==================================================
TARGET SUBJECT: {entity_name}
==================================================
{context_info}

==================================================
USER REQUEST:
==================================================
{user_content}

Hãy tạo câu hỏi củng cố hoặc đánh giá theo định dạng JSON bắt buộc.
"""

        ai_text = generate_text(prompt, api_key=custom_api_key)
        return ai_text


reinforcement_handler = ReinforcementHandler()
