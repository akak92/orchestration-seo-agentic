"""
state.py — Estado compartido del grafo.

RESPONSABILIDAD:
    Único lugar donde se declaran los campos del estado y sus reducers.
    Todos los nodos leen y escriben sobre este TypedDict.

CUÁNDO MODIFICAR:
    - Al añadir un campo nuevo que los nodos necesiten compartir.
    - Al cambiar la estrategia de combinación de un campo (reducer).

CONSEJOS:
    - Usa `Annotated[list[...], operator.add]` para campos que múltiples
      nodos actualizan en paralelo (fan-out). Sin reducer, solo se conserva
      el último valor escrito.
    - Usa `Annotated[list[BaseMessage], add_messages]` para el historial:
      este reducer desduplicó mensajes por ID y los añade en orden.
    - Campos escalares (str, int, bool) sin reducer se sobreescriben
      completamente en cada actualización — comportamiento correcto para
      flags como `next_agent` o `error`.
    - No pongas lógica de negocio aquí; solo tipos y reducers.
"""

import operator
from typing import Annotated
from typing_extensions import TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class SupervisorState(TypedDict):
    """
    Estado compartido entre el Supervisor y todos los agentes.

    Campos:
        messages    : Historial acumulativo de la conversación.
                      Reducer add_messages: añade sin duplicar por ID.
        next_agent  : Nombre del agente al que el Supervisor delega
                      en el próximo superstep. Vacío al iniciar.
        error       : Descripción del último error ocurrido, o None.
                      El error_handler lo consume y resetea a None.
        retry_count : Número de reintentos acumulados. Reducer operator.add
                      permite que cada reintento sume 1 sin sobreescribir.
    """
    messages:    Annotated[list[BaseMessage], add_messages]
    next_agent:  str
    error:       str | None
    retry_count: Annotated[int, operator.add]


# ---------------------------------------------------------------------------
# PLANTILLA PARA ESTADOS EXTENDIDOS
# ---------------------------------------------------------------------------
# Si tu proyecto necesita campos adicionales, extiende o reemplaza
# SupervisorState. Ejemplos de campos habituales:
#
#   # Acumular resultados parciales de workers en paralelo
#   partial_results: Annotated[list[str], operator.add]
#
#   # Metadatos del usuario o sesión
#   user_id:  str
#   language: str
#
#   # Contexto de negocio (sin reducer → siempre el último valor)
#   current_topic: str
#   task_type:     str
# ---------------------------------------------------------------------------
