from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    AIMessage,
    ToolMessage,
    BaseMessage
)

from langchain_core.language_models import BaseChatModel
from registry import AgentDescriptor, AgentType
from sanctum import SanctumManager
from tools import build_agent_tools
from tokens import add_usage, extract_usage


class AgentRuntime:
    '''
    Runtime base para agentes stateless.
    '''
    def __init__(
        self,
        descriptor: AgentDescriptor,
        llm: BaseChatModel,
        workspace_dir: str | None = None
    ):
        self.descriptor = descriptor
        self.llm = llm
        self.workspace_dir = workspace_dir
        self._last_usage: dict | None = None

    @staticmethod
    def _strip_frontmatter(text: str) -> str:
        '''Elimina el bloque YAML frontmatter --- ... --- del inicio del texto.'''
        ...

    def _system_prompt(
            self,
            extra_context: str = ""
    ) -> str:
        '''
        Construye el system prompt.
        Antepone un encabezado de contexto operacional para compatibilidad
        con modelos de razonamiento (o-series) que rechazan "adopta esta identidad".
        '''
        ...

    async def invoke(
        self,
        user_message: str,
        history: list[BaseMessage] | None = None,
        extra_content: str = "",
        attachments: dict[str, str] | None = None
    ) -> str:
        '''
        Método principal de ejecución del agente.
        Construye el prompt, llama al LLM y devuelve la respuesta.
        También extrae y almacena el uso de tokens para su consulta posterior.
        '''
        ...

    async def stream(
        self,
        user_message: str,
        history: list[BaseMessage] | None = None,
        extra_content: str = "",
        attachments: dict[str, str] | None = None
    ):
        '''
        Versión de invoke() que devuelve un generador para streaming de tokens.
        Extrae el uso de tokens al finalizar la generación.
        '''
        ...


class MemoryRuntime(AgentRuntime):
    '''
    Runtime para agentes memory.
    
    La única diferencia con AgentRuntime es que carga el sanctum
    (o first-breath.md en la primera sesión) como extra_context
    antes de delegar al super.
    '''
    def __init__(
        self,
        descriptor: AgentDescriptor,
        llm: BaseChatModel,
        sanctum: SanctumManager,
        team_id: str = 'default',
        workspace_dir: str | None = None
    ):
        super().__init__(descriptor, llm, workspace_dir)
        self.sanctum = sanctum
        self.team_id = team_id

    def _load_memory_context(self) -> str:
        '''Primera sesión → first-breath.md. Sesiones posteriores → sanctum completo.'''
        ...

    async def invoke(self, user_message, history=None, extra_context="", attachments=None) -> str:
        ...

    async def stream(self, user_message, history=None, extra_context="", attachments=None):
        ...


class AutonomousRuntime(MemoryRuntime):
    '''
    Runtime para agentes autónomos.
    
    Añade run_pulse() que lee PULSE.md del sanctum
    (o del skill como seed) y lo usa como extra_context.
    '''
    async def run_pulse(
        self,
        task: str | None = None
    ) -> str:
        '''
        Prioridad: PULSE.md en sanctum (configurable por el agente)
        Fallback: PULSE.md del skill (seed original)
        '''
        ...


def build_runtime(
    descriptor:    AgentDescriptor,
    llm:           BaseChatModel,
    sanctum:       SanctumManager,
    team_id:       str = "default",
    workspace_dir: str | None = None,
) -> AgentRuntime:
    """
    Factory que instancia el runtime correcto según agent_type.
    
    El workspace se aísla por team_id: workspace/{team_id}/
    → todos los agentes del mismo equipo comparten workspace
    → equipos distintos están completamente aislados
    """
    ...
