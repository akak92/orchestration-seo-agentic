from datetime import datetime

from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None   # None → crear nueva sesión


class ChatResponse(BaseModel):
    session_id: str
    thread_id: str
    response: str
    agent_used: str | None = None


class ChatMessageRead(BaseModel):
    id: str
    session_id: str
    role: str
    content: str
    agent_used: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatSessionRead(BaseModel):
    id: str
    thread_id: str
    title: str | None = None
    created_at: datetime
    last_message: str | None = None   # preview del último mensaje

    model_config = {"from_attributes": True}
