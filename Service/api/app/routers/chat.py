import uuid

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import httpx

from app.core.config import settings
from app.db.session import get_db
from app.models.user import User
from app.models.chat_session import ChatSession
from app.schemas.chat import ChatRequest, ChatResponse
from app.dependencies import get_current_user

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
    return ChatResponse(
        session_id=session.id,
        thread_id=session.thread_id,
        response=data["response"],
        agent_used=data.get("agent_used"),
    )


@router.post("/stream")
async def chat_stream(
    payload: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Streaming de la respuesta del agente via Server-Sent Events (SSE).
    El cliente debe leer el stream con EventSource o fetch reader.
    """
    session = await _get_or_create_session(current_user, payload.session_id, db)

    async def event_generator():
        async with httpx.AsyncClient(timeout=120) as client:
            async with client.stream(
                "POST",
                f"{settings.AGENT_SERVICE_URL}/stream",
                json={
                    "message":   payload.message,
                    "thread_id": session.thread_id,
                    "user_id":   current_user.id,
                },
            ) as resp:
                async for chunk in resp.aiter_text():
                    if chunk:
                        yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
