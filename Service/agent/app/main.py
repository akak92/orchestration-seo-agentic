"""
Service/agent — Punto de entrada del servicio de orquestación agéntica.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import StreamingResponse

from app.core.config import settings
from app.llm_factory import build_llm
from app.__core import AgentSpec, MultiAgentOrchestrator
from app.agents.editor import get_editor_spec
from app.agents.seo_optimizer import get_seo_optimizer_spec
from app.agents.summarizer import get_summarizer_spec
from app.api.schemas import AgentRequest, AgentResponse

logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

orchestrator: MultiAgentOrchestrator | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global orchestrator
    llm = build_llm()

    agents: list[AgentSpec] = [
        get_editor_spec(),
        get_seo_optimizer_spec(),
        get_summarizer_spec(),
    ]

    orchestrator = MultiAgentOrchestrator(llm=llm, agents=agents)

    logger.info("── Diagrama del grafo ──────────────────────────────")
    logger.info(orchestrator.get_graph_diagram())
    logger.info("Orquestador listo.")
    yield


app = FastAPI(
    title="Newsroom Agent Service",
    version="0.1.0",
    description="Servicio de orquestación agéntica (Supervisor + Editor + SEO Optimizer + Summarizer).",
    lifespan=lifespan,
)


@app.post("/invoke", response_model=AgentResponse)
async def invoke(req: AgentRequest):
    """Invocación bloqueante: espera la respuesta completa."""
    result = await orchestrator.invoke(
        message=req.message,
        thread_id=req.thread_id,
        user_id=req.user_id,
        session_id=req.session_id,
    )
    return AgentResponse(
        response=result["response"],
        agent_used=result.get("agent_used"),
        thread_id=req.thread_id,
    )


@app.post("/stream")
async def stream(req: AgentRequest):
    """Streaming via Server-Sent Events. Emite eventos JSON: routing, token, done."""
    async def event_generator():
        async for payload in orchestrator.stream_events(
            message=req.message,
            thread_id=req.thread_id,
            user_id=req.user_id,
            session_id=req.session_id,
        ):
            yield f"data: {payload}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.get("/health")
async def health():
    return {"status": "ok", "service": "agent"}
