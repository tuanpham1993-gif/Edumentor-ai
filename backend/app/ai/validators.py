
import json


def parse_ai_response(ai_text: str) -> dict:
    """
    Chuyển nội dung Gemini trả về thành JSON object
    và kiểm tra cấu trúc dữ liệu.
    """

    if not isinstance(ai_text, str) or not ai_text.strip():
        raise ValueError("Phản hồi AI đang trống")

    text = ai_text.strip()

    # Loại bỏ Markdown code fence nếu Gemini trả về
    if text.startswith("```"):
        lines = text.splitlines()

        if lines and lines[0].startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        text = "\n".join(lines).strip()

    # Chuyển JSON string thành Python dictionary
    try:
        response_data = json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"AI trả về JSON không hợp lệ: {e}") from e

    if not isinstance(response_data, dict):
        raise ValueError("Phản hồi AI phải là JSON object")

    # Kiểm tra answer
    answer = response_data.get("answer")

    if not isinstance(answer, str) or not answer.strip():
        raise ValueError("answer phải là chuỗi và không được để trống")

    # Kiểm tra reinforcement
    reinforcement = response_data.get("reinforcement")

    if not isinstance(reinforcement, dict):
        raise ValueError("reinforcement phải là object")

    explanation = reinforcement.get("explanation")
    example = reinforcement.get("example")

    if not isinstance(explanation, str):
        raise ValueError("reinforcement.explanation phải là chuỗi")

    if not isinstance(example, str):
        raise ValueError("reinforcement.example phải là chuỗi")

    # Kiểm tra related_skills
    related_skills = response_data.get("related_skills")

    if not isinstance(related_skills, list):
        raise ValueError("related_skills phải là danh sách")

    for skill in related_skills:
        if not isinstance(skill, dict):
            raise ValueError("Mỗi related_skill phải là object")

        if not isinstance(skill.get("name"), str):
            raise ValueError("related_skill thiếu name")

        if not isinstance(skill.get("prompt"), str):
            raise ValueError("related_skill thiếu prompt")

    # Kiểm tra suggested_questions
    suggested_questions = response_data.get("suggested_questions")

    if not isinstance(suggested_questions, list):
        raise ValueError("suggested_questions phải là danh sách")

    for question in suggested_questions:
        if not isinstance(question, str):
            raise ValueError("Mỗi suggested_question phải là chuỗi")

    # Trả về dữ liệu đã kiểm tra
    return {
        "answer": answer,
        "reinforcement": {
            "explanation": explanation,
            "example": example,
        },
        "related_skills": related_skills,
        "suggested_questions": suggested_questions,
    }
