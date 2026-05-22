from typing import Annotated
from fastapi import Depends

import sys
from pathlib import Path

# Añadir __core/ al path para que sus imports internos funcionen
sys.path.insert(0, str(Path(__file__).parent.parent / "__core"))

from __core.registry import AgentRegistry
from __core.sanctum import SanctumManager
from __core.llm_factory import build_llm
from langchain_core.language_models import BaseChatModel


# ── Singletons (se inicializan en el lifespan de main.py) ────────────────────

_registry: AgentRegistry | None = None
_sanctum: SanctumManager | None = None
_llm: BaseChatModel | None = None


def set_singletons(
    registry: AgentRegistry,
    sanctum: SanctumManager,
    llm: BaseChatModel
) -> None:
    '''Llamado una única vez desde el lifespan al arrancar la app.'''
    global _registry, _sanctum, _llm
    _registry = registry
    _sanctum = sanctum
    _llm = llm


# ── Funciones de dependencia para Depends() ───────────────────────────────────

def get_registry() -> AgentRegistry:
    ...


def get_sanctum() -> SanctumManager:
    ...


def get_llm() -> BaseChatModel:
    ...


# ── Tipos anotados (azúcar sintáctico para los routers) ───────────────────────

RegistryDep = Annotated[AgentRegistry, Depends(get_registry)]
SanctumDep  = Annotated[SanctumManager, Depends(get_sanctum)]
LLMDep      = Annotated[BaseChatModel, Depends(get_llm)]
