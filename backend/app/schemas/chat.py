from pydantic import BaseModel, Field
from uuid import UUID


class ChatSessionCreate(BaseModel):
    topic: str | None = None


class ChatMessageCreate(BaseModel):
    content: str = Field(min_length=1, max_length=5000)


class ChatMessageResponse(BaseModel):
    message_id: int
    role: str
    content: str


class ChatSessionResponse(BaseModel):
    session_id: UUID
    topic: str | None
    status: str