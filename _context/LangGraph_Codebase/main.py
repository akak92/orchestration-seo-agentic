"""
main.py — Punto de entrada del sistema multi-agente.

RESPONSABILIDAD:
    Configurar los agentes, instanciar el orquestador y ejecutar las tareas.
    Este archivo es la única pieza que cambia entre proyectos distintos;
    todo __core/ permanece reutilizable.

CUÁNDO MODIFICAR:
    - Al añadir, quitar o reconfigurar agentes para un nuevo caso de uso.
    - Al cambiar las tareas de demostración.
    - Al añadir un checkpointer persistente (SqliteSaver, PostgresSaver…).

CONSEJOS:
    - AgentSpec(name, prompt, tools=[]) para agentes sin herramientas.
    - AgentSpec(name, prompt, tools=[mi_tool]) para agentes con tool-loop.
    - El thread_id identifica la conversación en el checkpointer. Usa un
      ID único por usuario o sesión en producción.
    - stream_events es preferible a invoke cuando quieres mostrar progreso
      en tiempo real. Filtra los eventos que te interesen.
    - Llama a get_graph_diagram() al arrancar para verificar la topología
      del grafo antes de ejecutar consultas reales.

ESTRUCTURA RECOMENDADA:
    1. Inicializar LLM y herramientas.
    2. Definir los AgentSpec.
    3. Instanciar MultiAgentOrchestrator.
    4. (Opcional) Imprimir diagrama del grafo.
    5. Ejecutar tarea(s) con invoke o stream_events.
"""

import asyncio

from misc.llm_factory import build_llm
from __core import AgentSpec, MultiAgentOrchestrator


async def main() -> None:
    llm = build_llm()

    # ── 1. Definir herramientas (opcional) ────────────────────────────────
    # Ejemplo con DuckDuckGo (requiere: pip install ddgs)
    # from langchain_community.tools import DuckDuckGoSearchRun
    # search = DuckDuckGoSearchRun()

    # ── 2. Definir agentes ─────────────────────────────────────────────────
    agents = [
        AgentSpec(
            name="nombre_agente_1",
            prompt=(
                # TODO: describir el rol, especialidad y restricciones del agente.
                # Sé específico: ¿qué hace este agente? ¿qué NO debe hacer?
                "TODO: system prompt del agente 1"
            ),
            # tools=[search],   # ← descomenta si el agente necesita herramientas
        ),
        AgentSpec(
            name="nombre_agente_2",
            prompt=(
                "TODO: system prompt del agente 2"
            ),
        ),
        # Añade más AgentSpec según las necesidades del proyecto...
    ]

    # ── 3. Instanciar el orquestador ───────────────────────────────────────
    orchestrator = MultiAgentOrchestrator(
        llm=llm,
        agents=agents,
        # supervisor_prompt="...",  # opcional: prompt personalizado del Supervisor
        # checkpointer=...,         # opcional: checkpointer persistente
    )

    # ── 4. Verificar topología ─────────────────────────────────────────────
    print("── Diagrama del grafo ─────────────────────────────────")
    print(orchestrator.get_graph_diagram())

    # ── 5a. Invocación simple (bloqueante) ─────────────────────────────────
    result = await orchestrator.invoke(
        "TODO: escribe aquí la tarea del usuario",
        thread_id="sesion-001",
    )
    print("\n── Resultado ──────────────────────────────────────────")
    print(result)

    # ── 5b. Streaming de tokens (en tiempo real) ───────────────────────────
    print("\n── Streaming ──────────────────────────────────────────")
    current_node = ""
    async for event in orchestrator.stream_events(
        "TODO: escribe aquí otra tarea",
        thread_id="sesion-002",
    ):
        kind = event["event"]
        node = event.get("metadata", {}).get("langgraph_node", "")

        # Mostrar qué agente está activo
        if kind == "on_chain_start" and node and node != current_node:
            current_node = node
            if node not in ("__start__", "__end__"):
                print(f"\n[{node.upper()}]")

        # Mostrar tokens del LLM en tiempo real
        elif kind == "on_chat_model_stream":
            chunk = event["data"]["chunk"].content
            if chunk:
                print(chunk, end="", flush=True)

    print("\n")


asyncio.run(main())
