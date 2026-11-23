"""
Query decomposer module for Query Router.
Detects and splits compound queries into sub-queries.
"""

from app.ai.client import generate_text
from app.ai.query_router.normalizer import extract_json_object, normalize_text


def may_contain_multiple_requests(user_message: str) -> bool:
    """
    Kiểm tra sơ bộ xem tin nhắn có khả năng chứa
    nhiều yêu cầu độc lập hay không.
    """
    text = normalize_text(user_message)

    connectors = [
        " ngoai ra ",
        " ben canh do ",
        " dong thoi ",
        " them nua ",
        " them cho toi ",
        " sau do ",
        " tiep theo ",
        " khong nhung ",
        " ma con ",
        " cung nhu ",
        " and give me ",
        " and create ",
        " and provide ",
        " and test ",
        " va cho toi ",
        " va cho minh ",
        " va tao ",
        " va kiem tra ",
        ";",
        "\n",
    ]

    has_multiple_questions = user_message.count("?") > 1
    return any(connector in text for connector in connectors) or has_multiple_questions


def decompose_query_by_llm(user_message: str, custom_api_key: str | None = None) -> list[str]:
    """
    Dùng Gemini tách một tin nhắn thành các yêu cầu độc lập.
    Hàm này chỉ tách yêu cầu, không phân loại intent.
    """
    prompt = f"""
Bạn là Query Decomposer của EduMentor AI.

NHIỆM VỤ:
Phân tích tin nhắn người dùng và tách thành các yêu cầu
độc lập có thể cần xử lý riêng.

QUY TẮC:
1. Một tin nhắn có thể có một hoặc nhiều yêu cầu.
2. Không phụ thuộc vào dấu chấm, dấu phẩy hoặc dấu hỏi.
3. Hiểu các từ nối tiếng Việt như: ngoài ra, bên cạnh đó, thêm nữa, đồng thời, sau đó.
4. KHÔNG TÁCH các câu hỏi cùng ngữ cảnh hoặc yêu cầu giải thích kèm ví dụ:
   - "Giải thích Python và cho tôi ví dụ về vòng lặp" -> ĐÂY LÀ 1 YÊU CẦU DUY NHẤT.
   - "SQL là gì và cách sử dụng lệnh SELECT" -> ĐÂY LÀ 1 YÊU CẦU DUY NHẤT.
5. CHỈ TÁCH khi người dùng đưa ra các yêu cầu độc lập thực sự khác loại:
   - "Python là gì? Ngoài ra tìm giúp tôi các khóa học về Python" -> TÁCH THÀNH 2 YÊU CẦU.
6. Giữ nguyên ngữ cảnh và chủ đề chung.
7. Không tự thêm yêu cầu người dùng không nói.
8. Giữ nguyên tên công nghệ, Skill, Course.
9. Nếu chỉ có một yêu cầu, trả về đúng 1 phần tử.
10. Chỉ trả về JSON hợp lệ:

{{
    "queries": [
        "Yêu cầu thứ nhất",
        "Yêu cầu thứ hai"
    ]
}}

TIN NHẮN NGƯỜI DÙNG:
{user_message}
"""
    try:
        ai_text = generate_text(prompt, api_key=custom_api_key)
        result = extract_json_object(ai_text)
        queries = result.get("queries")

        if not isinstance(queries, list):
            raise ValueError("LLM không trả về danh sách queries.")

        cleaned_queries = []
        for query in queries:
            if not isinstance(query, str):
                continue
            query = query.strip()
            if query and query not in cleaned_queries:
                cleaned_queries.append(query)

        if not cleaned_queries:
            raise ValueError("Không tách được yêu cầu từ câu hỏi.")

        return cleaned_queries
    except Exception:
        # Fallback to rule-based connector splitting
        text = user_message
        for conn in [
            " and give me ",
            " and create ",
            " and provide ",
            " and test ",
            " va cho toi ",
            " va cho minh ",
            " va tao ",
            " va kiem tra ",
            " ngoài ra ",
            " bên cạnh đó ",
            " đồng thời ",
            ";",
            "\n",
        ]:
            if conn.lower() in text.lower():
                idx = text.lower().find(conn.lower())
                part1 = text[:idx].strip()
                # Keep action verb if conn contains give me/create/etc
                if "give me" in conn:
                    part2 = "give me " + text[idx + len(conn):].strip()
                elif "create" in conn:
                    part2 = "create " + text[idx + len(conn):].strip()
                elif "cho toi" in conn or "cho minh" in conn:
                    part2 = "cho toi " + text[idx + len(conn):].strip()
                elif "tao" in conn:
                    part2 = "tao " + text[idx + len(conn):].strip()
                else:
                    part2 = text[idx + len(conn):].strip()

                if part1 and part2:
                    return [part1, part2]

        return [user_message]
