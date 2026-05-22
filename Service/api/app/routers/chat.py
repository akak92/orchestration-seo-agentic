import json

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import httpx

from app.core.config import settings
from app.db.session import get_db, AsyncSessionFactory
from app.models.user import User
from app.models.chat_session import ChatSession
from app.models.chat_message import ChatMessage
from app.schemas.chat import ChatRequest, ChatResponse, ChatMessageRead, ChatSessionRead
from app.dependencies import get_current_user

_MAX_TITLE_LEN = 60


def _make_title(text: str) -> str:
    clean = text.replace("\n", " ").strip()
    return clean[:_MAX_TITLE_LEN] + ("\u2026" if len(clean) > _MAX_TITLE_LEN else "")

router = APIRouter()


async def _get_or_create_session(
    user: User, session_id: str | None, db: AsyncSession
) -> ChatSession:
    """Devuelve la sesión existente o crea una nueva."""
    if session_id:
        result = await db.execute(
            select(ChatSession).where(
                ChatSession.id == session_id,
                ChatSession.user_id == user.id,
            )
        )
        session = result.scalar_one_or_none()
        if not session:
            raise HTTPException(status_code=404, detail="Sesión no encontrada.")
        return session

    session = ChatSession(user_id=user.id)
    db.add(session)
    await db.flush()
    return session


@router.post("/", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Envía un mensaje al sistema agéntico y devuelve la respuesta completa."""
    session = await _get_or_create_session(current_user, payload.session_id, db)

    # Persistir mensaje del usuario
    db.add(ChatMessage(session_id=session.id, role="user", content=payload.message))

    # Auto-titular la sesión con el primer mensaje
    if not session.title:
        session.title = _make_title(payload.message)

    async with httpx.AsyncClient(timeout=120) as client:
        try:
            resp = await client.post(
                f"{settings.AGENT_SERVICE_URL}/invoke",
                json={
                    "message":    payload.message,
                    "thread_id":  session.thread_id,
                    "user_id":    current_user.id,
                },
            )
            resp.raise_for_status()
        except httpx.HTTPError as exc:
            raise HTTPException(status_code=502, detail=f"Error al contactar el servicio de agentes: {exc}")

    data = resp.json()

    # Persistir respuesta del asistente
    db.add(ChatMessage(
        session_id=session.id,
        role="assistant",
        content=data["response"],
        agent_used=data.get("agent_used"),
    ))
    await db.commit()

    return ChatResponse(
        session_id=session.id,
        thread_id=session.thread_id,
        response=data["response"],
        agent_used=data.get("agent_used"),
    )


# ── Historial de sesiones ──────────────────────────────────────────────

@router.get("/sessions", response_model=list[ChatSessionRead])
async def list_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Lista todas las sesiones del usuario, con preview del último mensaje."""
    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.user_id == current_user.id)
        .order_by(ChatSession.created_at.desc())
    )
    sessions = result.scalars().all()

    out: list[ChatSessionRead] = []
    for s in sessions:
        last_result = await db.execute(
            select(ChatMessage)
            .where(ChatMessage.session_id == s.id)
            .order_by(ChatMessage.created_at.desc())
            .limit(1)
        )
        last = last_result.scalar_one_or_none()
        out.append(ChatSessionRead(
            id=s.id,
            thread_id=s.thread_id,
            title=s.title,
            created_at=s.created_at,
            last_message=last.content[:80] if last else None,
        ))
    return out


@router.post("/sessions", response_model=ChatSessionRead, status_code=201)
async def create_session(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Crea una nueva sesión vacía."""
    session = ChatSession(user_id=current_user.id)
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return ChatSessionRead(
        id=session.id,
        thread_id=session.thread_id,
        title=session.title,
        created_at=session.created_at,
        last_message=None,
    )


@router.get("/sessions/{session_id}/messages", response_model=list[ChatMessageRead])
async def get_session_messages(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Devuelve todos los mensajes de una sesión."""
    sess_result = await db.execute(
        select(ChatSession).where(
            ChatSession.id == session_id,
            ChatSession.user_id == current_user.id,
        )
    )
    if not sess_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Sesión no encontrada.")

    msg_result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc())
    )
    return msg_result.scalars().all()


@router.delete("/sessions/{session_id}", status_code=204)
async def delete_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Elimina una sesión y todos sus mensajes."""
    result = await db.execute(
        select(ChatSession).where(
            ChatSession.id == session_id,
            ChatSession.user_id == current_user.id,
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Sesión no encontrada.")
    await db.delete(session)
    await db.commit()


@router.post("/stream")
async def chat_stream(
    payload: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Streaming via SSE. Emite eventos JSON:
      {"type":"session",  "session_id":"...", "thread_id":"..."}
      {"type":"routing",  "agent":"editor"|"seo_optimizer"|"summarizer"}
      {"type":"token",    "content":"..."}
      {"type":"done",     "agent_used":"..."}
    """
    session = await _get_or_create_session(current_user, payload.session_id, db)

    # Persistir mensaje del usuario antes de abrir el stream
    db.add(ChatMessage(session_id=session.id, role="user", content=payload.message))
    if not session.title:
        session.title = _make_title(payload.message)
    await db.commit()

    # Capturamos referencias en variables locales para usar dentro del generador
    # (la sesión SQLAlchemy del request puede cerrarse antes de que el generador acabe)
    session_id_snap = session.id
    thread_id_snap  = session.thread_id
    user_id_snap    = current_user.id
    message_snap    = payload.message

    async def event_gen():
        # Primer evento: el frontend puede actualizar el session_id incluso para nuevas sesiones
        yield (
            f"data: {json.dumps({'type': 'session', 'session_id': session_id_snap, 'thread_id': thread_id_snap})}\n\n"
        )

        response_chunks: list[str] = []
        agent_used_final: str | None = None

        try:
            async with httpx.AsyncClient(timeout=120) as client:
                async with client.stream(
                    "POST",
                    f"{settings.AGENT_SERVICE_URL}/stream",
                    json={
                        "message":    message_snap,
                        "thread_id":  thread_id_snap,
                        "user_id":    user_id_snap,
                        "session_id": session_id_snap,
                    },
                ) as resp:
                    async for line in resp.aiter_lines():
                        if not line.startswith("data: "):
                            continue
                        data_str = line[6:]
                        try:
                            data = json.loads(data_str)
                            t = data.get("type")
                            if t == "routing":
                                yield f"data: {data_str}\n\n"
                            elif t == "token":
                                response_chunks.append(data["content"])
                                yield f"data: {data_str}\n\n"
                            elif t == "done":
                                agent_used_final = data.get("agent_used")
                        except Exception:
                            pass
        except httpx.HTTPError as exc:
            yield f"data: {json.dumps({'type': 'error', 'detail': str(exc)})}\n\n"
            return

        # Persistir respuesta del asistente con una sesión DB fresca
        # (la sesión del request ya puede haber sido cerrada al llegar aquí)
        full_response = "".join(response_chunks)
        if full_response:
            async with AsyncSessionFactory() as persist_db:
                persist_db.add(ChatMessage(
                    session_id=session_id_snap,
                    role="assistant",
                    content=full_response,
                    agent_used=agent_used_final,
                ))
                await persist_db.commit()

        yield f"data: {json.dumps({'type': 'done', 'agent_used': agent_used_final})}\n\n"

    return StreamingResponse(event_gen(), media_type="text/event-stream")
