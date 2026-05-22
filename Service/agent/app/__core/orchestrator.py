from __future__ import annotations

from typing import AsyncIterator

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.language_models import BaseChatModel
from langgraph.checkpoint.memory import MemorySaver

from .state import SupervisorState
from .agent_spec import AgentSpec
from .graph import build_graph


class MultiAgentOrchestrator:
    """
    Punto de entrada del sistema multi-agente con patrón Supervisor.

    Uso:
        orchestrator = MultiAgentOrchestrator(llm=llm, agents=[...])
        result = await orchestrator.invoke(
            message="...",
            thread_id="user-123-session-456",
            user_id="user-123",
            session_id="session-456",
        )
    """

    def __init__(
        self,
        llm:               BaseChatModel,
        agents:            list[AgentSpec],
        supervisor_prompt: str | None = None,
        checkpointer=None,
    ):
        self._agents: dict[str, AgentSpec] = {spec.name: spec for spec in agents}
        sup_prompt = supervisor_prompt or self._default_supervisor_prompt(agents)
        self._graph = build_graph(
            llm          = llm,
            agents       = agents,
            sup_prompt   = sup_prompt,
            checkpointer = checkpointer or MemorySaver(),
        )

    @staticmethod
    def _default_supervisor_prompt(agents: list[AgentSpec]) -> str:
        agent_descriptions = "\n".join(
            f"- {spec.name}: {spec.description or spec.prompt[:120]}"
            for spec in agents
        )
        return (
            "Eres el Supervisor de un equipo de asistentes especializados para redactores de noticias. "
            "Tu única responsabilidad es analizar la solicitud del usuario y delegarla al agente correcto "
            "usando la herramienta `route_to_agent`. NO respondas directamente al usuario.\n\n"
            "Agentes disponibles:\n"
            f"{agent_descriptions}\n\n"
            "Si la tarea está completada o no corresponde a ningún agente, usa `route_to_agent` con next='__end__'.\n"
            "Si el usuario saluda o hace una pregunta general, usa '__end__' también.\n"
            "Responde siempre en el mismo idioma que el usuario."
        )

    def _initial_state(
        self,
        user_input: str,
        user_id: str = "",
        session_id: str = "",
    ) -> SupervisorState:
        return {
            "messages":    [HumanMessage(content=user_input)],
            "next_agent":  "",
            "error":       None,
            "retry_count": 0,
            "user_id":     user_id,
            "session_id":  session_id,
            "task_type":   "unknown",
        }

    async def invoke(
        self,
        message:    str,
        thread_id:  str = "default",
        user_id:    str = "",
        session_id: str = "",
    ) -> dict:
        """
        Ejecuta el grafo de forma bloqueante y devuelve la respuesta final.

        Returns:
            dict con 'response' (str) y 'agent_used' (str | None).
        """
        config = {"configurable": {"thread_id": thread_id}}
        initial_state = self._initial_state(message, user_id, session_id)

        final_state = await self._graph.ainvoke(initial_state, config=config)

        # Buscar hacia atrás el último AIMessage con contenido real
        agent_used = final_state.get("next_agent")
        for msg in reversed(final_state["messages"]):
            if isinstance(msg, AIMessage) and msg.content and not msg.tool_calls:
                return {"response": msg.content, "agent_used": agent_used}

        return {"response": "No se pudo obtener una respuesta.", "agent_used": agent_used}

    async def stream_events(
        self,
        message:    str,
        thread_id:  str = "default",
        user_id:    str = "",
        session_id: str = "",
    ) -> AsyncIterator[str]:
        """
        Async generator que emite los tokens de respuesta en tiempo real.
        Filtra solo eventos on_chat_model_stream de agentes (no del Supervisor).
        """
        config = {"configurable": {"thread_id": thread_id}}
        initial_state = self._initial_state(message, user_id, session_id)

        async for event in self._graph.astream_events(initial_state, config=config, version="v2"):
            if event["event"] == "on_chat_model_stream":
                # Ignorar tokens del nodo supervisor (son tool_calls de routing)
                node = event.get("metadata", {}).get("langgraph_node", "")
                if node == "supervisor":
                    continue
                chunk = event["data"]["chunk"]
                if chunk.content:
                    yield chunk.content

    def get_graph_diagram(self, xray: bool = False) -> str:
        return self._graph.get_graph(xray=xray).draw_mermaid()
