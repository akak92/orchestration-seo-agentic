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

    Topología:
        START → supervisor
        supervisor --Command--> [editor | seo_optimizer | summarizer | END]
        agente_N → supervisor
        supervisor --error--> error_handler
        error_handler --Command--> [supervisor | END]
    """
    agent_names = [spec.name for spec in agents]
    builder = StateGraph(SupervisorState)

    # Nodo Supervisor con política de reintentos ante fallos de API
    builder.add_node(
        "supervisor",
        build_supervisor_node(llm, agent_names, sup_prompt),
        retry=RetryPolicy(max_attempts=3),
    )

    # Nodo de manejo de errores
    builder.add_node("error_handler", build_error_handler_node())

    # Entrada: START → supervisor
    builder.add_edge(START, "supervisor")

    # Nodos de agentes: cada agente vuelve al supervisor al terminar
    for spec in agents:
        builder.add_node(spec.name, build_agent_node(llm, spec))
        builder.add_edge(spec.name, "supervisor")

    return builder.compile(
        checkpointer=checkpointer,
        # Red de seguridad: impide bucles infinitos aunque falle la
        # detección programática en el supervisor.
        interrupt_before=None,
    )
