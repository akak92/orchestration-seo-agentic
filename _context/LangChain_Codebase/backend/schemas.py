from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    team_id: str = "default"
    history: list[dict] | None = None        # Serialización de BaseMessage
    attachments: dict[str, str] | None = None


class ChatResponse(BaseModel):
    skill_id: str
    team_id: str
    response: str


class AgentInfo(BaseModel):
    '''Representación serializable de AgentDescriptor para la API.'''
    skill_id: str
    code: str
    name: str
    title: str
    icon: str
    description: str
    agent_type: str                          # "stateless" | "memory" | "autonomous"
    has_first_breath: bool
    has_pulse: bool


# ── Mensajes del protocolo WebSocket ──────────────────────────────────────────

class WsIncoming(BaseModel):
    '''Mensaje que envía el cliente por el WebSocket.'''
    message: str
    team_id: str = "default"
    history: list[dict] | None = None
    attachments: dict[str, str] | None = None


class WsChunk(BaseModel):
    '''Fragmento de token que el servidor envía al cliente.'''
    type: str = "chunk"                      # "chunk" | "end" | "error"
    content: str = ""
