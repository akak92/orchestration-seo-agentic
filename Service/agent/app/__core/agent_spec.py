from __future__ import annotations

from dataclasses import dataclass, field

from langchain_core.tools import BaseTool


@dataclass
class AgentSpec:
    """
    Configuración declarativa de un agente especializado.

    Atributos:
        name        : Identificador único del agente (sin espacios; es nombre de nodo).
        prompt      : System prompt del agente (rol, especialidad, restricciones).
        tools       : Herramientas disponibles. Si se proveen, el nodo tendrá
                      un tool-loop interno (llm → tools → llm).
        description : Descripción breve para el Supervisor. Debe indicar cuándo
                      delegar a este agente.
    """
    name:        str
    prompt:      str
    description: str = ""
    tools:       list[BaseTool] = field(default_factory=list)
