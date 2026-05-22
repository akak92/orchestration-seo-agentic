try:
    import tomllib
except ImportError:
    import tomli as tomllib

from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum


class AgentType(str, Enum):
    '''Enumeración para los tipos de agentes disponibles.'''
    STATELESS: str = "stateless"
    MEMORY: str = "memory"
    AUTONOMOUS: str = "autonomous"


@dataclass
class AgentDescriptor:
    '''
        Descriptor de un agente, con toda la información relevante extraída
        de su carpeta en skills/. 
        Este descriptor se utiliza para registrar el agente en el sistema 
        y para mostrar su información en la UI.
    '''

    skill_id: str                   # Nombre de carpeta en skills/
    skill_dir: Path                 # Ruta absoluta
    code: str                       # Alias corto
    name: str
    title: str
    icon: str
    description: str
    agent_type: AgentType
    skill_md: str                   # Contenido completo de SKILL.md
    has_first_breath: bool          # ¿Existe first-breath.md?
    has_pulse: bool                 # ¿Existe pulse.md?
    capabilities: list[dict] = field(default_factory=list)


class AgentRegistry:

    def __init__(self, skills_dir: str):
        self.skills_dir: Path = Path(skills_dir)
        self._agents: dict[str, AgentDescriptor] = {}

    def scan(self) -> None:
        '''
            Escanea el directorio de skills y registra todos los agentes válidos.
            Un skill es válido si tiene customize.toml con [agent] block + SKILL.md.
        '''
        ...

    def all(self) -> list[AgentDescriptor]:
        ...

    def get(self, skill_id: str) -> AgentDescriptor | None:
        ...

    def count(self) -> int:
        ...
