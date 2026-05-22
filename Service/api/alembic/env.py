"""
env.py — Entorno de ejecución de Alembic.

Configura el motor de base de datos y ejecuta las migraciones.
Soporta modo offline (genera SQL) y online async (aplica directamente).

La URL se lee desde la variable de entorno DATABASE_URL_SYNC para no
depender de la URL hardcodeada en alembic.ini.
"""
import asyncio
import os
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context

# ── Importar todos los modelos para que Alembic los detecte ──────────────────
# Esto es lo que hace posible el --autogenerate
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.base import Base  # noqa: F401 — importa todos los modelos vía db/base.py

# ── Configuración de Alembic ──────────────────────────────────────────────────
config = context.config

# URL async (con +asyncpg) para el engine. Tiene prioridad sobre alembic.ini.
# DATABASE_URL_SYNC se usa solo como fallback convirtiendo el esquema.
async_db_url = os.environ.get("DATABASE_URL") or os.environ.get(
    "DATABASE_URL_SYNC", ""
).replace("postgresql://", "postgresql+asyncpg://")

if async_db_url:
    # Guardar también la versión síncrona en sqlalchemy.url para el modo offline
    sync_url = async_db_url.replace("postgresql+asyncpg://", "postgresql://")
    config.set_main_option("sqlalchemy.url", sync_url)

# Configurar logging desde alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# MetaData objetivo para el autogenerate
target_metadata = Base.metadata


# ── Modo offline: genera SQL sin conectarse ───────────────────────────────────
def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


# ── Modo online async: aplica migraciones directamente ───────────────────────
def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Crea el motor async con asyncpg y ejecuta las migraciones."""
    connectable = create_async_engine(
        async_db_url,
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


# ── Punto de entrada ──────────────────────────────────────────────────────────
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
