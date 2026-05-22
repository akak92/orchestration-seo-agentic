"""
agent_spec.py — Especificación declarativa de un agente especializado.

RESPONSABILIDAD:
    Dataclass de configuración pura. No contiene lógica, solo describe
    qué es un agente: cómo se llama, qué instrucciones tiene y qué
    herramientas puede usar.

CUÁNDO MODIFICAR:
    - Al añadir metadatos a los agentes (ej. descripción para el Supervisor,
      temperatura propia, modelo alternativo).
    - Al cambiar el tipo de las herramientas admitidas.

CONSEJOS:
    - Mantén este archivo sin imports de LangGraph; solo depende de
      langchain_core. Así es fácil de testear de forma aislada.
    - El campo `prompt` es el system prompt que recibe el agente en cada
      llamada. Sé específico: indica el rol, el tono y lo que NO debe hacer.
    - Si un agente necesita herramientas, pásalas aquí. build_agent_node
      en nodes.py detectará si `tools` está poblado y creará un subgrafo
      con tool-loop interno automáticamente.
    - Para agentes sin herramientas, deja `tools` vacío (default).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from langchain_core.tools import BaseTool


@dataclass
class AgentSpec:
    """
    Configuración declarativa de un agente especializado.

    Atributos:
        name   : Identificador único del agente. Se usa como nombre de nodo
                 en el grafo, por lo que debe ser un string sin espacios.
        prompt : System prompt del agente. Define su rol, especialidad
                 y restricciones de comportamiento.
        tools  : Herramientas que el agente puede invocar. Si se proveen,
                 build_agent_node creará un subgrafo con tool-loop interno
                 (llm → tools → llm) en lugar de un nodo simple.
    """
    name:   str
    prompt: str
    tools:  list[BaseTool] = field(default_factory=list)


# ---------------------------------------------------------------------------
# PLANTILLA PARA AGENTES CON METADATOS EXTENDIDOS
# ---------------------------------------------------------------------------
# Si necesitas más control por agente, añade campos opcionales:
#
# @dataclass
# class AgentSpec:
#     name:        str
#     prompt:      str
#     tools:       list[BaseTool] = field(default_factory=list)
#     description: str = ""          # para que el Supervisor sepa cuándo usarlo
#     model:       str | None = None # modelo alternativo para este agente
#     temperature: float = 0.7       # temperatura propia del agente
# ---------------------------------------------------------------------------
