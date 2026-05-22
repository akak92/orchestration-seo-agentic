"""
Herramientas de memoria para los agentes.

Cada agente puede usar estas tools para:
  - Leer/guardar preferencias de estilo del usuario (PostgreSQL, largo plazo).
  - Leer/guardar contexto de la sesión activa (Redis, corto plazo).

El user_id se inyecta en el estado del grafo y los agentes lo pasan
explícitamente al invocar las tools.
"""
import json
import logging

import asyncpg
import redis.asyncio as aioredis
from langchain_core.tools import tool

from app.core.config import settings

logger = logging.getLogger(__name__)


# ── PostgreSQL — Memoria de largo plazo (preferencias del usuario) ────────────

async def _get_pg_connection():
    return await asyncpg.connect(settings.DATABASE_URL_SYNC)


@tool
async def save_user_preference(user_id: str, key: str, value: str) -> str:
    """
    Guarda una preferencia de estilo o dato relevante del usuario en la base de datos.
    Úsala cuando el usuario exprese una preferencia explícita (ej. tono formal,
    no usar anglicismos, longitud preferida de resúmenes, etc.).

    Args:
        user_id : ID del usuario.
        key     : Clave de la preferencia (ej. 'tone', 'max_summary_words').
        value   : Valor de la preferencia.
    """
    try:
        conn = await _get_pg_connection()
        async with conn.transaction():
            await conn.execute(
                """
                INSERT INTO user_preferences (user_id, key, value, updated_at)
                VALUES ($1, $2, $3, NOW())
                ON CONFLICT (user_id, key)
                DO UPDATE SET value = EXCLUDED.value, updated_at = NOW()
                """,
                user_id, key, value,
            )
        await conn.close()
        return f"Preferencia '{key}' guardada para el usuario {user_id}."
    except Exception as exc:
        logger.error(f"Error guardando preferencia: {exc}")
        return f"No se pudo guardar la preferencia: {exc}"


@tool
async def get_user_preferences(user_id: str) -> str:
    """
    Recupera todas las preferencias de estilo guardadas del usuario.
    Úsala al inicio de cada tarea para personalizar la respuesta.

    Args:
        user_id: ID del usuario.
    """
    try:
        conn = await _get_pg_connection()
        rows = await conn.fetch(
            "SELECT key, value FROM user_preferences WHERE user_id = $1", user_id
        )
        await conn.close()
        if not rows:
            return "El usuario no tiene preferencias guardadas aún."
        prefs = {row["key"]: row["value"] for row in rows}
        return json.dumps(prefs, ensure_ascii=False)
    except Exception as exc:
        logger.error(f"Error leyendo preferencias: {exc}")
        return f"No se pudieron recuperar las preferencias: {exc}"


# ── Redis — Memoria de corto plazo (contexto de sesión activa) ────────────────

def _redis_client():
    return aioredis.from_url(settings.REDIS_URL, decode_responses=True)


@tool
async def save_session_context(session_id: str, key: str, value: str) -> str:
    """
    Guarda un dato de contexto para la sesión activa en Redis.
    TTL de 24 horas. Úsala para guardar el texto que el usuario está trabajando,
    resultados intermedios o notas temporales.

    Args:
        session_id : ID de la sesión de chat.
        key        : Clave del contexto (ej. 'current_text', 'last_seo_keywords').
        value      : Valor a guardar.
    """
    try:
        redis = _redis_client()
        redis_key = f"session:{session_id}:{key}"
        await redis.setex(redis_key, 86400, value)  # TTL: 24h
        await redis.aclose()
        return f"Contexto '{key}' guardado para sesión {session_id}."
    except Exception as exc:
        logger.error(f"Error guardando contexto en Redis: {exc}")
        return f"No se pudo guardar el contexto: {exc}"


@tool
async def get_session_context(session_id: str, key: str) -> str:
    """
    Recupera un dato de contexto de la sesión activa desde Redis.

    Args:
        session_id : ID de la sesión de chat.
        key        : Clave del contexto a recuperar.
    """
    try:
        redis = _redis_client()
        redis_key = f"session:{session_id}:{key}"
        value = await redis.get(redis_key)
        await redis.aclose()
        if value is None:
            return f"No hay contexto guardado para la clave '{key}' en esta sesión."
        return value
    except Exception as exc:
        logger.error(f"Error leyendo contexto de Redis: {exc}")
        return f"No se pudo recuperar el contexto: {exc}"
