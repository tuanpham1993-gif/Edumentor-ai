"""
Code Handler module for EduMentor AI.
Specialized handler for code analysis, bug fixing, error debugging,
and programming explanations using Gemini.
"""

from app.ai.client import generate_text

CODE_SYSTEM_PROMPT = """
Bạn là Trợ lý Lập trình & Sửa lỗi chuyên sâu (Code Expert & Mentor) của EduMentor AI.

NHIỆM VỤ:
1. Phân tích mã nguồn người học cung cấp (Python, JavaScript, SQL, C++, Java, v.v.).
2. Giải thích rõ nguyên nhân lỗi (SyntaxError, Runtime, IndexError, Logic bug, v.v.).
3. Cung cấp phiên bản code đã sửa hoàn chỉnh, có comment rõ ràng.
4. Hướng dẫn các phương pháp thực hành tốt nhất (best practices) và cách tối ưu hiệu năng.

QUY TẮC PHẢN HỒI:
1. Luôn định dạng Markdown rõ ràng cho các khối code (ví dụ: ```python ... ```).
2. Giải thích ngắn gọn, đi thẳng vào trọng tâm vấn đề.
3. Chỉ trả về JSON hợp lệ với cấu trúc bắt buộc:
{
    "answer": "Nội dung giải thích chi tiết, code đã fix và lưu ý (định dạng Markdown)",
    "suggestions": [
        {"label": "Tối ưu code này", "prompt": "Hãy giúp tôi tối ưu độ phức tạp thuật toán của đoạn code trên"},
        {"label": "Viết Unit Test", "prompt": "Hãy viết test case kiểm thử cho hàm này"}
    ]
}
4. suggestions chứa tối đa 3 gợi ý ngắn gọn, hữu ích.
5. Không thêm văn bản bên ngoài khối JSON.
"""


class CodeHandler:
    """
    Code Handler analyzes, explains, and fixes code for learners.
    """

    def handle(
        self,
        route_result: dict,
        user_content: str,
        conversation_history: str,
        custom_api_key: str | None = None,
    ) -> str:
        """
        Xử lý yêu cầu về code bằng Gemini với prompt chuyên biệt.
        """
        task_type = route_result.get("task_type", "code_analysis")
        intent = route_result.get("intent", "code_help")

        specific_instruction = ""
        if task_type == "code_fix" or intent == "code_fix":
            specific_instruction = """
YÊU CẦU ĐẶC BIỆT:
- Người học đang gặp lỗi hoặc muốn sửa code.
- Hãy chỉ ra chính xác dòng code bị lỗi và lý do tại sao dòng đó gây lỗi.
- Cung cấp đoạn code đã sửa hoàn chỉnh để người học có thể copy và chạy được ngay.
"""
        elif task_type == "code_analysis" or intent == "code_analysis":
            specific_instruction = """
YÊU CẦU ĐẶC BIỆT:
- Người học muốn phân tích hoặc giải thích code.
- Hãy phân tích luồng thực thi (execution flow), biến số, và độ phức tạp thuật toán (Time/Space Complexity).
"""

        prompt = f"""
{CODE_SYSTEM_PROMPT}

==================================================
CONVERSATION HISTORY
==================================================

{conversation_history}

==================================================
USER REQUEST
==================================================

{user_content}

==================================================
TASK TYPE: {task_type}
==================================================
{specific_instruction}

Hãy trả lời theo định dạng JSON bắt buộc.
"""

        ai_text = generate_text(prompt, api_key=custom_api_key)
        return ai_text


code_handler = CodeHandler()
