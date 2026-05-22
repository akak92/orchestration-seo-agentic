from pydantic import BaseModel


class AgentRequest(BaseModel):
    message:    str
    thread_id:  str
    user_id:    str
    session_id: str = ""


class AgentResponse(BaseModel):
    response:   str
    agent_used: str | None = None
    thread_id:  str
