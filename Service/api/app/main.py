"""
Service/api — FastAPI service
Punto de entrada de la aplicación.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.session import engine, Base
from app.routers import auth, users, chat, documents, internal


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Crear tablas si no existen (en producción usar Alembic)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="Newsroom Agentic API",
    version="0.1.0",
    description="API de orquestación agéntica para redactores de canal de noticias.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,      prefix="/auth",      tags=["auth"])
app.include_router(users.router,     prefix="/users",     tags=["users"])
app.include_router(chat.router,      prefix="/chat",      tags=["chat"])
app.include_router(documents.router, prefix="/documents", tags=["documents"])
app.include_router(internal.router, prefix="/internal",  tags=["internal"])


@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok", "service": "api"}
