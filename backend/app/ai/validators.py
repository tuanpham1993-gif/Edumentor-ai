
import json


MAX_SUGGESTIONS = 3


def parse_ai_response(ai_text: str) -> dict:
    """
    Chuyển nội dung Gemini trả về thành JSON object
    và kiểm tra cấu trúc dữ liệu mới.

    Cấu trúc:
    {
        "answer": "Nội dung trả lời",
        "suggestions": [
            {
                "label": "Tên nút",
                "prompt": "Câu hỏi gửi đến AI"
            }
        ]
    }
    """

    if not isinstance(ai_text, str) or not ai_text.strip():
        raise ValueError("Phản hồi AI đang trống")

    text = ai_text.strip()

    # Loại bỏ Markdown code fence nếu Gemini trả về
    if text.startswith("```"):
        lines = text.splitlines()

        if lines and lines[0].strip().startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        text = "\n".join(lines).strip()

    # Chuyển JSON string thành Python dictionary
    try:
        response_data = json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"AI trả về JSON không hợp lệ: {e}"
        ) from e

    if not isinstance(response_data, dict):
        raise ValueError("Phản hồi AI phải là JSON object")

    # Kiểm tra answer
    answer = response_data.get("answer")

    if not isinstance(answer, str):
        raise ValueError("answer phải là chuỗi")

    if not answer.strip():
        raise ValueError("answer không được để trống")

    # Kiểm tra suggestions
    suggestions = response_data.get("suggestions")

    if not isinstance(suggestions, list):
        raise ValueError("suggestions phải là danh sách")

    if len(suggestions) > MAX_SUGGESTIONS:
        raise ValueError(
            f"Chỉ được tạo tối đa {MAX_SUGGESTIONS} gợi ý"
        )

    validated_suggestions = []

    for index, item in enumerate(suggestions):

        if not isinstance(item, dict):
            raise ValueError(
                f"suggestions[{index}] phải là object"
            )

        label = item.get("label")
        prompt = item.get("prompt")

        if not isinstance(label, str) or not label.strip():
            raise ValueError(
                f"suggestions[{index}].label không hợp lệ"
            )

        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError(
                f"suggestions[{index}].prompt không hợp lệ"
            )

        validated_suggestions.append({
            "label": label.strip(),
            "prompt": prompt.strip(),
        })

    # Chỉ trả về các trường thuộc cấu trúc đã quy định
    return {
        "answer": answer.strip(),
        "suggestions": validated_suggestions,
    }
