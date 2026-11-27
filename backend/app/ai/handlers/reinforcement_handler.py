"""
Reinforcement Handler module for EduMentor AI.
Generates knowledge reinforcement exercises, multiple-choice quizzes,
and practice questions for skills and courses using Gemini.
"""

import json
from typing import Any

from app.ai.client import generate_text
from app.ai.query_router.normalizer import normalize_text

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

QUY TẮC BẮT BUỘC VỀ PHẠM VI CHỦ ĐỀ (DOMAIN SCOPE):
- EduMentor CHỈ hỗ trợ ôn tập các kỹ năng và kiến thức trong lĩnh vực: CÔNG NGHỆ THÔNG TIN, LẬP TRÌNH, KHOA HỌC MÁY TÍNH, KỸ THUẬT PHẦN MỀM, CƠ SỞ DỮ LIỆU, TRÍ TUỆ NHÂN TẠO / MACHINE LEARNING, VÀ CÁC KHÓA HỌC TRONG NỀN TẢNG EDUMENTOR.
- TUYỆT ĐỐI TỪ CHỐI các chủ đề ngoài phạm vi như: Đầu tư tài chính / chứng khoán, tiền tệ, bất động sản, nấu ăn, tử vi / bói toán, giải trí, đời tư cá nhân, chính trị, y tế,...
- Khi người học yêu cầu ôn tập hoặc ra đề thi về chủ đề ngoài phạm vi:
  BẮT BUỘC PHẢI TỪ CHỐI LỊCH SỰ, giải thích rằng EduMentor chỉ hỗ trợ ôn tập về lập trình và công nghệ thông tin, đồng thời gợi ý các kỹ năng công nghệ thực tế (như Python, SQL, React, Web Development, Machine Learning,...).

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


def check_out_of_scope_reinforcement(text: str, entity_name: str = "") -> dict[str, Any] | None:
    """
    Kiểm tra nhanh chủ đề yêu cầu ôn tập có nằm ngoài phạm vi học tập / CNTT của EduMentor hay không.
    (Ví dụ: chứng khoán, tiền tệ, nấu ăn, tử vi, bói toán, showbiz...)
    """
    combined = f"{text} {entity_name}"
    normalized = normalize_text(combined)

    out_of_scope_categories = [
        (
            "chứng khoán / tài chính",
            [
                "chung khoan",
                "trung khoan",
                "co phieu",
                "trai phieu",
                "forex",
                "dau tu tai chinh",
                "bat dong san",
                "tien ao",
                "crypto",
                "bitcoin",
            ],
        ),
        ("nấu ăn / ẩm thực", ["nau an", "cong thuc nau", "mon an ngon", "am thuc"]),
        ("tử vi / phong thủy", ["tu vi", "boi toan", "phong thuy", "xem boi", "cung hoang dao"]),
        ("làm đẹp / thẩm mỹ", ["lam dep", "trang diem", "phau thuat tham my"]),
        ("giải trí / showbiz", ["showbiz", "nguoi noi tieng", "tin tuc ngoi sao"]),
    ]

    for category_name, keywords in out_of_scope_categories:
        for kw in keywords:
            if kw in normalized:
                return {
                    "answer": (
                        f"Xin lỗi bạn, EduMentor là nền tảng cố vấn học tập và phát triển kỹ năng chuyên sâu về "
                        f"**Lập trình, Khoa học máy tính và Công nghệ thông tin**.\n\n"
                        f"Hệ thống hiện tại không hỗ trợ nội dung ôn tập thuộc lĩnh vực **{category_name}** nằm ngoài phạm vi này. "
                        f"Nếu bạn muốn ôn tập kiến thức về các kỹ năng công nghệ như **Python, JavaScript, Cơ sở dữ liệu (SQL), "
                        f"Cấu trúc dữ liệu & Giải thuật, Web Development, Machine Learning**... bạn cứ nhắn cho mình nhé!"
                    ),
                    "suggestions": [
                        {"label": "Ôn tập Python", "prompt": "Cho tôi câu hỏi trắc nghiệm ôn tập về Python"},
                        {"label": "Ôn tập SQL", "prompt": "Cho tôi câu hỏi trắc nghiệm ôn tập về SQL cơ bản"},
                        {"label": "AI Lộ trình", "prompt": "Hướng dẫn tôi tạo lộ trình trên trang AI Lộ trình"},
                    ],
                }
    return None


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
    ) -> str | dict[str, Any]:
        """
        Xử lý yêu cầu ôn tập, trắc nghiệm và củng cố kiến thức bằng Gemini.
        """
        entity_name = route_result.get("entity_name") or "kiến thức tổng quát"

        # 1. Kiểm tra chủ đề ngoài phạm vi CNTT / lập trình
        out_of_scope = check_out_of_scope_reinforcement(user_content, entity_name)
        if out_of_scope is not None:
            return out_of_scope

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
