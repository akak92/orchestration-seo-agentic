"""
routing.py — Tool de routing dinámico para el Supervisor.

RESPONSABILIDAD:
    Construir y devolver el @tool que el Supervisor llama para decidir
    a qué agente delegar. La descripción se genera dinámicamente en
    runtime a partir de la lista de agentes registrados.

CUÁNDO MODIFICAR:
    - Al cambiar la firma de la herramienta (ej. añadir campo `priority`).
    - Al añadir validaciones adicionales sobre el agente elegido.
    - Al cambiar el formato del mensaje de retorno.

CONSEJOS:
    - La descripción del tool es lo que el LLM lee para saber qué valores
      son válidos. Asegúrate de que sea clara y enumere exactamente los
      nombres de los agentes disponibles más "FINISH".
    - El parámetro `reason` obliga al LLM a razonar antes de decidir
      (chain-of-thought implícito). No lo elimines aunque no lo uses.
    - Si el LLM elige un agente inválido, la función devuelve un error
      descriptivo. El Supervisor lo leerá y deberá corregir en el siguiente
      turno — no lances excepciones aquí.
    - Este tool NUNCA se ejecuta realmente como herramienta externa;
      es un mecanismo de routing. Por eso en nodes.py se añade un
      ToolMessage sintético tras cada tool_call del Supervisor.
"""

from langchain_core.tools import BaseTool, tool


def make_route_tool(agent_names: list[str]) -> BaseTool:
    """
    Construye el tool de routing con las opciones disponibles en runtime.

    Args:
        agent_names: Lista de nombres de agentes registrados en el grafo.
                     "FINISH" se añade automáticamente como opción de cierre.

    Returns:
        Un @tool con descripción dinámica lista para bind_tools al LLM.
    """
    valid_options: str = ...  # TODO: construir string con las opciones válidas

    @tool
    def route_to_agent(agent: str, reason: str) -> str:
        """Delega la tarea al agente indicado. Opciones definidas en la descripción."""
        ...  # TODO: validar `agent` y devolver mensaje de routing

    # TODO: sobrescribir route_to_agent.description con valid_options

    return route_to_agent
