from __future__ import annotations

from langchain_core.messages import AIMessage, SystemMessage, ToolMessage
from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool, tool
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.types import Command

from .state import SupervisorState
from .agent_spec import AgentSpec

MAX_RETRIES: int = 3


# ── Supervisor ────────────────────────────────────────────────────────────────

def build_supervisor_node(
    llm:         BaseChatModel,
    agent_names: list[str],
    sup_prompt:  str,
):
    """
    Construye el nodo Supervisor.

    Usa un tool de routing (route_to_agent) para decidir a qué agente delegar
    o si terminar. Devuelve un Command que actualiza el estado y fija el
    siguiente nodo simultáneamente.
    """

    @tool
    def route_to_agent(next: str) -> str:
        """
        Enruta la conversación al agente correcto o finaliza.

        Args:
            next: Nombre del agente destino, o '__end__' para terminar.
        """
        return next

    bound_llm = llm.bind_tools([route_to_agent])

    async def supervisor_node(state: SupervisorState) -> Command:
        messages = [SystemMessage(content=sup_prompt)] + state["messages"]
        response = await bound_llm.ainvoke(messages)

        # Extraer el destino del tool_call
        if response.tool_calls:
            tool_call = response.tool_calls[0]
            destination = tool_call["args"].get("next", "__end__")
        else:
            destination = "__end__"

        # ToolMessage sintético — requerido por la API de OpenAI
        tool_msg = ToolMessage(
            content=f"Enrutando a: {destination}",
            tool_call_id=response.tool_calls[0]["id"] if response.tool_calls else "no_call",
        )

        goto = END if destination == "__end__" else destination

        return Command(
            update={
                "messages":   [response, tool_msg],
                "next_agent": destination,
                "error":      None,
            },
            goto=goto,
        )

    return supervisor_node


# ── Error handler ─────────────────────────────────────────────────────────────

def build_error_handler_node():
    """
    Construye el nodo global de manejo de errores.
    Reintenta hasta MAX_RETRIES veces; luego termina con mensaje de fallo.
    """

    async def error_handler_node(state: SupervisorState) -> Command:
        error   = state.get("error", "Error desconocido.")
        retries = state.get("retry_count", 0)

        if retries < MAX_RETRIES:
            correction_msg = AIMessage(
                content=f"[Sistema] Reintentando tras error: {error}. Intento {retries + 1}/{MAX_RETRIES}."
            )
            return Command(
                update={
                    "messages":    [correction_msg],
                    "error":       None,
                    "retry_count": 1,
                },
                goto="supervisor",
            )

        failure_msg = AIMessage(
            content=f"Lo siento, no pude completar la tarea después de {MAX_RETRIES} intentos. "
                    f"Por favor, inténtalo de nuevo más tarde."
        )
        return Command(
            update={
                "messages":    [failure_msg],
                "error":       None,
                "retry_count": 0,
            },
            goto=END,
        )

    return error_handler_node


# ── Agente especializado ──────────────────────────────────────────────────────

def build_agent_node(llm: BaseChatModel, spec: AgentSpec):
    """
    Construye el nodo de un agente especializado.

    - Sin herramientas → función async simple.
    - Con herramientas → subgrafo compilado con tool-loop interno.
    """

    if not spec.tools:
        # Agente simple sin herramientas
        async def _simple_node(state: SupervisorState) -> dict:
            messages = [SystemMessage(content=spec.prompt)] + state["messages"]
            try:
                response = await llm.ainvoke(messages)
                # Prefijar con el nombre del agente para trazabilidad
                prefixed = AIMessage(content=f"[{spec.name}] {response.content}")
                return {"messages": [prefixed], "error": None}
            except Exception as exc:
                return {"error": str(exc)}

        return _simple_node

    # Agente con herramientas — subgrafo interno con tool-loop
    agent_llm = llm.bind_tools(spec.tools)

    async def _llm_node(state: SupervisorState) -> dict:
        messages = [SystemMessage(content=spec.prompt)] + state["messages"]
        try:
            response = await agent_llm.ainvoke(messages)
            return {"messages": [response]}
        except Exception as exc:
            return {"error": str(exc)}

    subgraph = StateGraph(SupervisorState)
    subgraph.add_node("llm",   _llm_node)
    subgraph.add_node("tools", ToolNode(spec.tools))

    subgraph.add_edge(START, "llm")
    subgraph.add_conditional_edges("llm", tools_condition)
    subgraph.add_edge("tools", "llm")

    return subgraph.compile()
