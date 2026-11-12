
import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import Users
from app.models.chat_session import ChatSession
from app.models.chat_message import ChatMessage
from app.schemas.chat import ChatSessionCreate, ChatMessageCreate
from app.services.tutor_service import process_chat_message


logger = logging.getLogger(__name__)


# ==========================================
# ROUTER
# ==========================================

# Router dành cho người dùng đã đăng nhập
router = APIRouter(
    prefix="/chat/sessions",
    tags=["Chat Tutor"],
)

# Router dành cho khách chưa đăng nhập
public_router = APIRouter(
    prefix="/chat",
    tags=["Public Chat Tutor"],
)


# ==========================================
# HELPER: KIỂM TRA QUYỀN SỞ HỮU PHIÊN CHAT
# ==========================================

def get_owned_session(
    db: Session,
    session_id: UUID,
    user_id: int,
):
    """
    Chỉ lấy phiên chat thuộc về người dùng đang đăng nhập.

    Nếu phiên không tồn tại hoặc thuộc người khác,
    đều trả về 404.
    """

    session = (
        db.query(ChatSession)
        .filter(
            ChatSession.session_id == session_id,
            ChatSession.user_id == user_id,
        )
        .first()
    )

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy phiên chat",
        )

    return session


# ==========================================
# 1. TẠO PHIÊN CHAT
# ==========================================

@router.post("")
def create_session(
    data: ChatSessionCreate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    session = ChatSession(
        user_id=current_user.user_id,
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
    current_user: Users = Depends(get_current_user),
):
    # Kiểm tra phiên chat có thuộc người đăng nhập không.
    get_owned_session(
        db=db,
        session_id=session_id,
        user_id=current_user.user_id,
    )

    try:
        response_data = process_chat_message(
            db=db,
            session_id=session_id,
            user_content=data.content,
            allow_sql_retrieval=True,
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
        db.rollback()

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
    current_user: Users = Depends(get_current_user),
):
    sessions = (
        db.query(ChatSession)
        .filter(
            ChatSession.user_id == current_user.user_id
        )
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
    current_user: Users = Depends(get_current_user),
):
    session = get_owned_session(
        db=db,
        session_id=session_id,
        user_id=current_user.user_id,
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
    current_user: Users = Depends(get_current_user),
):
    # Phải kiểm tra quyền trước khi lấy tin nhắn.
    get_owned_session(
        db=db,
        session_id=session_id,
        user_id=current_user.user_id,
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
    current_user: Users = Depends(get_current_user),
):
    session = get_owned_session(
        db=db,
        session_id=session_id,
        user_id=current_user.user_id,
    )

    db.delete(session)
    db.commit()

    return {
        "message": "Đã xóa phiên chat",
    }


# ==========================================
# 7. CHAT CÔNG KHAI - KHÔNG CẦN ĐĂNG NHẬP
# ==========================================

@public_router.post("/ask")
def ask_public(
    data: ChatMessageCreate,
    db: Session = Depends(get_db),
):
    """
    Khách chưa đăng nhập vẫn có thể hỏi AI.

    - Không cần access token.
    - Không tạo ChatSession.
    - Không lưu ChatMessage.
    - Không truy vấn SQL dữ liệu cá nhân.
    - Vẫn có thể sử dụng RAG/Qdrant.
    """

    try:
        response_data = process_chat_message(
            db=db,
            session_id=None,
            user_content=data.content,
            allow_sql_retrieval=False,
        )

        return {
            "session_id": None,
            "user_message": data.content,
            "assistant_message": response_data,
            "saved": False,
        }

    except ValueError as e:
        logger.error(
            "PUBLIC AI RESPONSE VALIDATION ERROR: %s",
            e,
        )

        raise HTTPException(
            status_code=502,
            detail=f"Phản hồi AI không hợp lệ: {str(e)}",
        )

    except Exception as e:
        db.rollback()

        logger.exception("PUBLIC CHATBOT ERROR: %s", e)

        raise HTTPException(
            status_code=502,
            detail="Không thể xử lý yêu cầu với AI. Vui lòng thử lại sau.",
        )
