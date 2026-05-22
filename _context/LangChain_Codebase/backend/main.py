from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI

from backend.dependencies import set_singletons
from backend.routers import agents, chat

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "__core"))

from __core.registry import AgentRegistry
from __core.sanctum import SanctumManager
from __core.llm_factory import build_llm

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR:      Path = Path(__file__).parent.parent   # 04_Codebase/
SKILLS_DIR:    Path = BASE_DIR / "skills"
STORAGE_DIR:   Path = BASE_DIR / "storage"
WORKSPACE_DIR: Path = BASE_DIR / "workspace"


# ── Lifespan: inicialización y limpieza de singletons ─────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    '''
    Se ejecuta una vez al arrancar la app.
    Inicializa registry, sanctum y llm, y los inyecta en dependencies.py.
    '''
    registry = AgentRegistry(str(SKILLS_DIR))
    registry.scan()

    sanctum = SanctumManager(str(STORAGE_DIR))
    llm     = build_llm()

    set_singletons(registry, sanctum, llm)

    yield
    # Limpieza al apagar (si es necesaria)


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Generic Agentic API",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(agents.router)
app.include_router(chat.router)


@app.get("/health")
def health():
    return {"status": "ok"}
