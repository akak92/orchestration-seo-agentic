from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None   # None → crear nueva sesión


class ChatResponse(BaseModel):
    session_id: str
    thread_id: str
    response: str
    agent_used: str | None = None
