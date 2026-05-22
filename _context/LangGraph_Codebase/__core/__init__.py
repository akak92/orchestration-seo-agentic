"""
__core/__init__.py — Re-exports de la API pública del orquestador.

Permite importar desde __core directamente:
    from __core import AgentSpec, MultiAgentOrchestrator

CONSEJO:
    Mantén __all__ actualizado. Solo exporta lo que el llamador externo
    (main.py) necesita. Los módulos internos (state, nodes, graph…)
    no necesitan estar aquí.
"""

from .state import SupervisorState
from .agent_spec import AgentSpec
from .orchestrator import MultiAgentOrchestrator

__all__ = ["SupervisorState", "AgentSpec", "MultiAgentOrchestrator"]
