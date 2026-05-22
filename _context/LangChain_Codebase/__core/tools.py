from pathlib import Path
from langchain_core.tools import tool
from sanctum import SanctumManager


def build_agent_tools(
    skill_id: str,
    sanctum_manager: SanctumManager | None = None,
    workspace_dir: str | None = None,
    team_id: str = 'default'
) -> list:
    '''
        Construye las LangChain tools para un agente.
        
        El skill_id y team_id quedan capturados en closures —
        el agente no puede manipular qué sanctum o workspace usa.
    '''
    ...


def _safe_resolve(workspace_root: Path, user_path: str) -> Path:
    '''
    Seguridad: path traversal prevention

    Resuelve user_path relativo a workspace_root y verifica que
    el resultado siga dentro del sandbox.
    
    .resolve() expande todos los .. y symlinks → ruta canónica absoluta.
    
    Sin esta verificación:
        user_path = "../../etc/passwd"
        (workspace_root / user_path) = /app/workspace/../../etc/passwd
        → .resolve() = /etc/passwd  ← FUERA del sandbox
        → str(/etc/passwd).startswith(str(/app/workspace/)) = False
        → ValueError ✓
    '''
    ...
