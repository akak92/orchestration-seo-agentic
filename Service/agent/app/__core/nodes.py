from __future__ import annotations

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool, tool
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.types import Command

from .state import SupervisorState
from .agent_spec import AgentSpec

MAX_RETRIES: int = 3
MAX_TOOL_CALLS: int = 6  # máximo de rondas tool-loop por agente


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

    def _agent_already_responded(messages: list, agent_names: list[str]) -> bool:
        """
        Comprueba si algún agente ya respondió tras el último HumanMessage.
        Los agentes prefijan su respuesta con '[nombre]', lo que permite
        esta detección sin llamar al LLM.
        """
        # Encontrar el índice del último HumanMessage
        last_human_idx = -1
        for i, msg in enumerate(messages):
            if isinstance(msg, HumanMessage):
                last_human_idx = i

        if last_human_idx < 0:
            return False

        # Buscar AIMessage de agente posterior al último HumanMessage
        for msg in messages[last_human_idx + 1:]:
            if isinstance(msg, AIMessage) and msg.content and not msg.tool_calls:
                if any(msg.content.startswith(f"[{name}]") for name in agent_names):
                    return True
        return False

    async def supervisor_node(state: SupervisorState) -> Command:
        # Detección programática: si un agente ya respondió, terminamos sin
        # invocar al LLM (evita el bucle supervisor → agente → supervisor → ...)
        if _agent_already_responded(state["messages"], agent_names):
            return Command(
                update={"next_agent": "__end__", "error": None},
                goto=END,
            )

        messages = [SystemMessage(content=sup_prompt)] + state["messages"]
        response = await bound_llm.ainvoke(messages)

        # Extraer el destino del tool_call
        if response.tool_calls:
            tool_call = response.tool_calls[0]
            destination = tool_call["args"].get("next", "__end__")
            # ToolMessage sintético — requerido por la API de OpenAI
            tool_msg = ToolMessage(
                content=f"Enrutando a: {destination}",
                tool_call_id=tool_call["id"],
            )
            update_msgs = [response, tool_msg]
        else:
            # El LLM respondió sin usar la tool → terminar directamente
            destination = "__end__"
            update_msgs = [response]

        goto = END if destination == "__end__" else destination

        # Cuando terminamos sin que ningún agente haya respondido (p.ej. saludos
        # o consultas genéricas), añadir un mensaje de bienvenida/fallback para
        # que el orquestador siempre tenga una respuesta que devolver al usuario.
        if goto == END and not _agent_already_responded(state["messages"], agent_names):
            fallback = AIMessage(
                content=(
                    "[supervisor] ¡Hola! Soy el asistente de redacción del canal de noticias. "
                    "Puedo ayudarte con:\n"
                    "• **Corrección** de textos (ortografía, gramática y estilo periodístico)\n"
                    "• **Optimización SEO** (keywords, títulos, meta descripción)\n"
                    "• **Resúmenes** (ejecutivo, bullet points, lead periodístico, redes sociales)\n\n"
                    "Comparte el texto con el que quieres trabajar y te indicaré qué hacer."
                )
            )
            update_msgs = update_msgs + [fallback]

        return Command(
            update={
                "messages":   update_msgs,
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
                # Prefijar con el nombre del agente — necesario para que el
                # supervisor detecte programáticamente que la tarea está hecha.
                prefixed = AIMessage(content=f"[{spec.name}] {response.content}")
                return {"messages": [prefixed], "error": None}
            except Exception as exc:
                return {"error": str(exc)}

        return _simple_node

    # Agente con herramientas — subgrafo interno con tool-loop
    agent_llm = llm.bind_tools(spec.tools)

    async def _llm_node(state: SupervisorState) -> dict:
        # Contar cuántas rondas de tool-calls ya ocurrieron en esta invocación
        # para evitar bucles infinitos si las tools devuelven resultados ambiguos.
        tool_rounds = sum(
            1 for msg in state["messages"]
            if isinstance(msg, ToolMessage)
        )
        if tool_rounds >= MAX_TOOL_CALLS:
            # Forzar respuesta sin tool-calls
            stop_msg = SystemMessage(
                content="Has usado suficientes herramientas. Responde ahora directamente al usuario."
            )
            messages = [SystemMessage(content=spec.prompt)] + state["messages"] + [stop_msg]
        else:
            messages = [SystemMessage(content=spec.prompt)] + state["messages"]

        try:
            response = await agent_llm.ainvoke(messages)
            # Si es la respuesta final (sin tool-calls), prefijar con el nombre
            # del agente para que el supervisor la detecte.
            if response.content and not response.tool_calls:
                response = AIMessage(
                    content=f"[{spec.name}] {response.content}",
                    id=response.id,
                )
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
