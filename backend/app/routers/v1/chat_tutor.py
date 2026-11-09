
import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.chat_session import ChatSession
from app.models.chat_message import ChatMessage
from app.schemas.chat import ChatSessionCreate, ChatMessageCreate
from app.services.tutor_service import process_chat_message

router = APIRouter(prefix="/chat/sessions", tags=["Chat Tutor"])

logger = logging.getLogger(__name__)


# ==========================================
# 1. TẠO PHIÊN CHAT
# ==========================================

@router.post("")
def create_session(
    data: ChatSessionCreate,
    db: Session = Depends(get_db),
):
    session = ChatSession(
        user_id=None,
        topic=data.topic,
        session_type="tutor",
        status="active",
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    return {
        "session_id": session.session_id,
        "topic": session.topic,
        "status": session.status,
    }


# ==========================================
# 2. GỬI TIN NHẮN CHO GIA SƯ AI
# ==========================================

@router.post("/{session_id}/messages")
def send_message(
    session_id: UUID,
    data: ChatMessageCreate,
    db: Session = Depends(get_db),
):
    # Kiểm tra phiên chat
    session = db.query(ChatSession).filter(
        ChatSession.session_id == session_id
    ).first()

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy phiên chat",
        )

    try:
        # Gọi Service xử lý toàn bộ nghiệp vụ chatbot
        response_data = process_chat_message(
            db=db,
            session_id=session_id,
            user_content=data.content,
        )

        return {
            "session_id": session_id,
            "user_message": data.content,
            "assistant_message": response_data,
        }

    except ValueError as e:
        logger.error("AI RESPONSE VALIDATION ERROR: %s", e)

        raise HTTPException(
            status_code=502,
            detail=f"Phản hồi AI không hợp lệ: {str(e)}",
        )

    except Exception as e:
        logger.exception("CHATBOT ERROR: %s", e)

        raise HTTPException(
            status_code=502,
            detail="Không thể xử lý yêu cầu với AI. Vui lòng thử lại sau.",
        )


# ==========================================
# 3. LẤY DANH SÁCH PHIÊN CHAT
# ==========================================

@router.get("")
def list_sessions(
    db: Session = Depends(get_db),
):
    sessions = (
        db.query(ChatSession)
        .filter(ChatSession.user_id.is_(None))
        .order_by(ChatSession.created_at.desc())
        .all()
    )

    return [
        {
            "session_id": session.session_id,
            "topic": session.topic,
            "status": session.status,
        }
        for session in sessions
    ]


# ==========================================
# 4. LẤY CHI TIẾT PHIÊN CHAT
# ==========================================

@router.get("/{session_id}")
def get_session(
    session_id: UUID,
    db: Session = Depends(get_db),
):
    session = db.query(ChatSession).filter(
        ChatSession.session_id == session_id
    ).first()

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy phiên chat",
        )

    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(
            ChatMessage.created_at.asc(),
            ChatMessage.message_id.asc(),
        )
        .all()
    )

    return {
        "session_id": session.session_id,
        "topic": session.topic,
        "status": session.status,
        "messages": [
            {
                "message_id": message.message_id,
                "role": message.role,
                "content": message.content,
                "created_at": message.created_at,
            }
            for message in messages
        ],
    }


# ==========================================
# 5. LẤY LỊCH SỬ TIN NHẮN
# ==========================================

@router.get("/{session_id}/messages")
def list_messages(
    session_id: UUID,
    db: Session = Depends(get_db),
):
    session = db.query(ChatSession).filter(
        ChatSession.session_id == session_id
    ).first()

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy phiên chat",
        )

    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(
            ChatMessage.created_at.asc(),
            ChatMessage.message_id.asc(),
        )
        .all()
    )

    return [
        {
            "message_id": message.message_id,
            "role": message.role,
            "content": message.content,
            "created_at": message.created_at,
        }
        for message in messages
    ]


# ==========================================
# 6. XÓA PHIÊN CHAT
# ==========================================

@router.delete("/{session_id}")
def delete_session(
    session_id: UUID,
    db: Session = Depends(get_db),
):
    session = db.query(ChatSession).filter(
        ChatSession.session_id == session_id
    ).first()

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy phiên chat",
        )

    db.delete(session)
    db.commit()

    return {
        "message": "Đã xóa phiên chat",
    }
