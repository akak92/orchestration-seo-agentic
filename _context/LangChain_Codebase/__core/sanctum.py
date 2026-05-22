from pathlib import Path
from datetime import datetime

STANDARD_FILES: list[str] = [
    'INDEX.md',
    'PERSONA.md',
    'CREED.md',
    'BOND.md',
    'MEMORY.md',
    'CAPABILITIES.md'
]

class SanctumManager:
    '''
        Gestor de archivos en el "sanctum" de cada agente.
        El sanctum es un espacio de almacenamiento persistente para cada agente,
        donde se guardan sus archivos de configuración, memoria y registros de sesiones.
            Estructura típica del sanctum:
        sanctum/
            └── team_id/
                └── skill_id/
                    ├── MEMORY.md          # Memoria persistente del agente (Markdown)
                    ├── INDEX.md           # Información general del agente (Markdown)
                    ├── PERSONA.md         # Detalles de la personalidad del agente (Markdown)
                    ├── CREED.md           # Principios o reglas del agente (Markdown)
                    ├── BOND.md            # Relaciones o vínculos del agente (Markdown)
                    ├── CAPABILITIES.md    # Capacidades y herramientas del agente (Markdown)
                    └── sessions/          # Carpeta para logs de sesiones
                        └── YYYY-MM-DD.md  # Log de una sesión específica (Markdown)
    '''

    def __init__(self, sanctum_root: str):
        self.root = Path(sanctum_root)

    def sanctum_path(self, skill_id: str, team_id: str = 'default') -> Path:
        ...

    def is_first_breath(self, skill_id: str, team_id: str = 'default') -> bool:
        '''True si MEMORY.md no existe → primera sesión del agente con este equipo.'''
        ...

    def load(self, skill_id: str, files: list[str] | None = None,
              team_id: str = 'default') -> str:
        '''
            Concatena los archivos del sanctum como un bloque de contexto Markdown.
            Se inyecta en el extra_context del system prompt vía MemoryRuntime.
        '''
        ...

    def save_file(
            self,
            skill_id: str,
            filename: str,
            content: str,
            team_id: str = 'default',
    ) -> None:
        ...

    def read_file(
            self,
            skill_id: str,
            filename: str,
            team_id: str = 'default'
    ) -> str | None:
        ...

    def append_session_log(
            self,
            skill_id: str,
            content: str,
            teamd_id: str = 'default'
    ) -> None:
        ...
