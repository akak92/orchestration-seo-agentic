import sys
import asyncio
from pathlib import Path

# ── Resolver rutas base ────────────────────────────────────────────────────────
BASE_DIR: Path = Path(__file__).parent           # 04_Codebase/
CORE_DIR: Path = BASE_DIR / "__core"

# Añadir __core/ al path para que sus imports internos funcionen
sys.path.insert(0, str(CORE_DIR))

# ── Imports de __core/ ────────────────────────────────────────────────────────
from __core.registry import AgentRegistry, AgentDescriptor
from __core.sanctum import SanctumManager
from __core.runtime import AgentRuntime, build_runtime
from __core.llm_factory import build_llm

# ── Paths del entorno de prueba ───────────────────────────────────────────────
SKILLS_DIR:    Path = BASE_DIR / "skills"
STORAGE_DIR:   Path = BASE_DIR / "storage"
WORKSPACE_DIR: Path = BASE_DIR / "workspace"

TEAM_ID = "default"


# ── Setup ─────────────────────────────────────────────────────────────────────
def setup():
    '''Instancia los componentes compartidos: registry, llm y sanctum.'''
    ...


# ── Test 1: AgentRuntime (stateless) ─────────────────────────────────────────
async def test_stateless(registry: AgentRegistry, llm, sanctum: SanctumManager):
    ...


# ── Test 2: MemoryRuntime ─────────────────────────────────────────────────────
async def test_memory(registry: AgentRegistry, llm, sanctum: SanctumManager):
    ...


# ── Test 3: AutonomousRuntime (pulse) ─────────────────────────────────────────
async def test_autonomous(registry: AgentRegistry, llm, sanctum: SanctumManager):
    ...


# ── Test 4: Streaming ─────────────────────────────────────────────────────────
async def test_streaming(registry: AgentRegistry, llm, sanctum: SanctumManager):
    ...


# ── Entry point ───────────────────────────────────────────────────────────────
async def main():
    ...


if __name__ == "__main__":
    asyncio.run(main())
