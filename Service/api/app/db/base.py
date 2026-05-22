"""
Importa todos los modelos para que Alembic los descubra automáticamente
en el autogenerate de migraciones.
"""
from app.db.session import Base  # noqa: F401

from app.models.user import User          # noqa: F401
from app.models.chat_session import ChatSession  # noqa: F401
from app.models.chat_message import ChatMessage  # noqa: F401
from app.models.document import Document          # noqa: F401
from app.models.user_preference import UserPreference  # noqa: F401
