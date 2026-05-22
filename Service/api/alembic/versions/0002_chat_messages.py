"""Agregar tabla chat_messages para historial de conversaciones.

Revision ID: 0002_chat_messages
Revises: 0001_initial
Create Date: 2026-05-22
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0002_chat_messages"
down_revision: Union[str, None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "chat_messages",
        sa.Column("id",         sa.String(36),  nullable=False),
        sa.Column("session_id", sa.String(36),  nullable=False),
        sa.Column("role",       sa.String(16),  nullable=False),
        sa.Column("content",    sa.Text(),      nullable=False),
        sa.Column("agent_used", sa.String(64),  nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["session_id"], ["chat_sessions.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_chat_messages_session_id", "chat_messages", ["session_id"])


def downgrade() -> None:
    op.drop_index("ix_chat_messages_session_id", table_name="chat_messages")
    op.drop_table("chat_messages")
