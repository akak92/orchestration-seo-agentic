"""
orchestrator.py — API pública del sistema multi-agente.

RESPONSABILIDAD:
    Capa delgada que inicializa los componentes y expone la interfaz
    pública del orquestador. Toda la lógica de construcción del grafo
    está delegada en graph.py.

CUÁNDO MODIFICAR:
    - Al añadir nuevos métodos públicos (ej. get_state, update_state).
    - Al cambiar la firma de invoke o stream_events.
    - Al añadir soporte para múltiples checkpointers o stores.

CONSEJOS:
    - _default_supervisor_prompt genera el prompt del Supervisor a partir
      de los AgentSpec registrados. Si pasas supervisor_prompt explícito
      en __init__, este método no se llama.
    - _initial_state centraliza la construcción del estado inicial. Si
      añades campos al SupervisorState, actualiza este método también.
    - invoke devuelve el último AIMessage con contenido real (sin tool_calls).
      Recorre el historial al revés para encontrarlo, descartando ToolMessages
      y AIMessages de routing (que tienen tool_calls pero no content).
    - stream_events es un async generator que yield-ea cada evento del grafo.
      El llamador decide qué filtrar (on_chat_model_stream, on_tool_start…).
    - get_graph_diagram es útil para depuración y documentación. Pasa
      xray=True para ver también los nodos internos de los subgrafos.
"""

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

    Uso básico:
        orchestrator = MultiAgentOrchestrator(llm=llm, agents=[...])
        result = await orchestrator.invoke("tu tarea aquí", thread_id="sesion-001")
    """

    def __init__(
        self,
        llm:               BaseChatModel,
        agents:            list[AgentSpec],
        supervisor_prompt: str | None = None,
        checkpointer=None,
    ):
        """
        Args:
            llm:               Modelo de lenguaje compartido por todos los nodos.
            agents:            Lista de AgentSpec con los agentes disponibles.
            supervisor_prompt: Prompt del Supervisor. Si es None, se genera
                               automáticamente a partir de los agentes.
            checkpointer:      Checkpointer para persistencia entre invocaciones.
                               Por defecto MemorySaver (en memoria, sin persistir).
        """
        self._agents: dict[str, AgentSpec] = {spec.name: spec for spec in agents}
        sup_prompt = supervisor_prompt or self._default_supervisor_prompt()
        self._graph = build_graph(
            llm          = llm,
            agents       = agents,
            sup_prompt   = sup_prompt,
            checkpointer = checkpointer or MemorySaver(),
        )

    def _default_supervisor_prompt(self) -> str:
        """Genera el prompt del Supervisor listando los agentes disponibles."""
        ...  # TODO: construir prompt descriptivo con nombre y prompt[:80] de cada agente

    def _initial_state(self, user_input: str) -> SupervisorState:
        """Construye el estado inicial para una nueva invocación."""
        ...  # TODO: devolver dict con messages, next_agent, error, retry_count

    async def invoke(self, user_input: str, thread_id: str = "default") -> str:
        """
        Ejecuta el grafo de forma bloqueante y devuelve la respuesta final.

        Busca hacia atrás en el historial el último AIMessage con contenido
        real (sin tool_calls), descartando mensajes de routing del Supervisor.

        Args:
            user_input: Tarea o pregunta del usuario.
            thread_id:  Identificador de la conversación (para checkpointer).

        Returns:
            Contenido de texto del último mensaje útil del agente.
        """
        ...  # TODO: ainvoke + recorrer messages al revés buscando AIMessage con content

    async def stream_events(
        self,
        user_input: str,
        thread_id:  str = "default",
    ) -> AsyncIterator:
        """
        Ejecuta el grafo en modo streaming y yield-ea cada evento.

        Eventos útiles para filtrar en el llamador:
            "on_chat_model_stream" → tokens del LLM (event["data"]["chunk"].content)
            "on_chain_start"       → nodo activo (event["metadata"]["langgraph_node"])
            "on_tool_start"        → herramienta invocada
            "on_tool_end"          → resultado de la herramienta

        Args:
            user_input: Tarea o pregunta del usuario.
            thread_id:  Identificador de la conversación.
        """
        ...  # TODO: astream_events(version="v2") + yield cada evento

    def get_graph_diagram(self) -> str:
        """
        Devuelve el diagrama Mermaid del grafo compilado.

        Útil para depuración y documentación. xray=True muestra también
        los nodos internos de los subgrafos (ej. tool-loop del researcher).
        """
        return self._graph.get_graph(xray=True).draw_mermaid()
