import operator
from typing import Annotated
from typing_extensions import TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class SupervisorState(TypedDict):
    """
    Estado compartido entre el Supervisor y todos los agentes.

    Campos estándar:
        messages    : Historial acumulativo. Reducer add_messages (sin duplicados).
        next_agent  : Nombre del agente al que el Supervisor delega.
        error       : Descripción del último error, o None.
        retry_count : Reintentos acumulados.

    Campos extendidos (contexto de usuario/sesión):
        user_id     : ID del usuario autenticado. Necesario para que las
                      herramientas de memoria accedan al perfil correcto.
        session_id  : ID de la sesión/conversación activa.
        task_type   : Clasificación de la tarea detectada por el Supervisor
                      ("correction" | "seo" | "summary" | "unknown").
    """
    messages:    Annotated[list[BaseMessage], add_messages]
    next_agent:  str
    error:       str | None
    retry_count: Annotated[int, operator.add]

    # Contexto de sesión
    user_id:    str
    session_id: str
    task_type:  str
