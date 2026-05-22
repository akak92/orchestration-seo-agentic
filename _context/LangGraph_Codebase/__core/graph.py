"""
graph.py — Construcción y cableado del StateGraph.

RESPONSABILIDAD:
    Función pura que recibe todos los componentes ya construidos y devuelve
    el grafo compilado. No contiene lógica de negocio; solo registra nodos
    y aristas.

CUÁNDO MODIFICAR:
    - Al añadir nuevos nodos (ej. un nodo de logging o de contexto).
    - Al cambiar la política de reintentos del Supervisor.
    - Al cambiar el checkpointer (ej. de MemorySaver a SqliteSaver).

CONSEJOS:
    - Mantén build_graph como función pura: recibe parámetros, devuelve
      el grafo compilado. No accedas a variables globales ni efectos
      secundarios aquí.
    - El nodo "supervisor" usa Command internamente, así que NO necesita
      add_conditional_edges. Las aristas supervisor → agente las gestiona
      Command en runtime.
    - El nodo "error_handler" tampoco necesita aristas explícitas hacia
      el Supervisor; Command las maneja dinámicamente.
    - Todos los agentes sí necesitan add_edge(spec.name, "supervisor")
      porque su retorno es siempre fijo: volver al Supervisor.
    - RetryPolicy en el nodo supervisor añade resiliencia ante fallos
      transitorios de la API (rate limits, timeouts). Ajusta los parámetros
      según el SLA de tu deployment.
    - Para producción, sustituye MemorySaver por AsyncSqliteSaver u otro
      checkpointer persistente. El grafo compilado no cambia.
"""

from __future__ import annotations

from langchain_core.language_models import BaseChatModel
from langgraph.graph import StateGraph, START
from langgraph.types import RetryPolicy

from .state import SupervisorState
from .agent_spec import AgentSpec
from .nodes import build_supervisor_node, build_error_handler_node, build_agent_node


def build_graph(
    llm:         BaseChatModel,
    agents:      list[AgentSpec],
    sup_prompt:  str,
    checkpointer,
):
    """
    Cablea el StateGraph del patrón Supervisor y devuelve el grafo compilado.

    Topología resultante:
        START → supervisor
        supervisor --Command--> [agente_1 | agente_2 | ... | END]
        agente_N → supervisor
        supervisor --error--> error_handler
        error_handler --Command--> [supervisor | END]

    Args:
        llm:         Modelo de lenguaje compartido por todos los nodos.
        agents:      Lista de AgentSpec con los agentes a registrar.
        sup_prompt:  System prompt del Supervisor.
        checkpointer: Checkpointer para persistencia (MemorySaver, SqliteSaver…).

    Returns:
        CompiledGraph listo para ainvoke / astream_events.
    """
    agent_names: list[str] = [spec.name for spec in agents]
    builder = StateGraph(SupervisorState)

    # TODO: registrar nodo "supervisor" con RetryPolicy
    # TODO: registrar nodo "error_handler"
    # TODO: add_edge(START, "supervisor")
    # TODO: bucle for spec in agents → registrar agente + add_edge(spec.name, "supervisor")
    # TODO: builder.compile(checkpointer=checkpointer)

    ...
