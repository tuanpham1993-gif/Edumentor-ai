
import json
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.chat_message import ChatMessage
from app.ai.client import generate_text
from app.ai.prompts.tutor import TUTOR_SYSTEM_PROMPT
from app.ai.validators import parse_ai_response


def process_chat_message(
    db: Session,
    session_id: UUID,
    user_content: str,
) -> dict:
    """
    Xử lý nghiệp vụ gửi tin nhắn cho gia sư AI.

    1. Lưu câu hỏi người dùng.
    2. Lấy lịch sử hội thoại.
    3. Tạo prompt cho Gemini.
    4. Nhận và kiểm tra phản hồi AI.
    5. Lưu câu trả lời AI.
    """

    # 1. Lưu câu hỏi người dùng
    user_message = ChatMessage(
        session_id=session_id,
        role="user",
        content=user_content,
    )

    db.add(user_message)
    db.commit()

    # 2. Lấy lịch sử hội thoại
    history = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(
            ChatMessage.created_at.asc(),
            ChatMessage.message_id.asc(),
        )
        .all()
    )

    conversation_lines = []

    for message in history:
        content = message.content

        # Nếu là câu trả lời AI dạng JSON,
        # chỉ lấy answer để đưa vào lịch sử hội thoại.
        if message.role == "assistant":
            try:
                saved_response = json.loads(content)

                if isinstance(saved_response, dict):
                    content = saved_response.get("answer", content)

            except (json.JSONDecodeError, TypeError):
                pass

        role_name = (
            "Người dùng"
            if message.role == "user"
            else "Gia sư AI"
        )

        conversation_lines.append(
            f"{role_name}: {content}"
        )

    conversation = "\n".join(conversation_lines)

    # 3. Tạo prompt hoàn chỉnh
    prompt = f"""
{TUTOR_SYSTEM_PROMPT}

Dưới đây là lịch sử hội thoại giữa người học và gia sư AI:

{conversation}

Hãy trả lời câu hỏi mới nhất của người học
dựa trên lịch sử hội thoại và tuân thủ chính xác cấu trúc JSON đã quy định.
"""

    # 4. Gọi Gemini và kiểm tra phản hồi
    ai_text = generate_text(prompt)

    print("GEMINI RAW RESPONSE:", repr(ai_text))

    response_data = parse_ai_response(ai_text)

    # 5. Lưu câu trả lời AI
    ai_message = ChatMessage(
        session_id=session_id,
        role="assistant",
        content=json.dumps(
            response_data,
            ensure_ascii=False,
        ),
    )

    db.add(ai_message)
    db.commit()
    db.refresh(ai_message)

    return response_data
