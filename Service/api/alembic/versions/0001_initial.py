"""Migración inicial — Crear todas las tablas del sistema.

Revision ID: 0001_initial
Revises:
Create Date: 2026-05-22
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── users ──────────────────────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id",              sa.String(36),  nullable=False),
        sa.Column("email",           sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("full_name",       sa.String(255), nullable=True),
        sa.Column("is_active",       sa.Boolean(),   nullable=False, server_default="true"),
        sa.Column("is_superuser",    sa.Boolean(),   nullable=False, server_default="false"),
        sa.Column("created_at",      sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at",      sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_users_email", "users", ["email"])

    # ── chat_sessions ──────────────────────────────────────────────────────
    op.create_table(
        "chat_sessions",
        sa.Column("id",         sa.String(36), nullable=False),
        sa.Column("thread_id",  sa.String(36), nullable=False),
        sa.Column("user_id",    sa.String(36), nullable=False),
        sa.Column("title",      sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("thread_id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_chat_sessions_user_id", "chat_sessions", ["user_id"])

    # ── documents ─────────────────────────────────────────────────────────
    op.create_table(
        "documents",
        sa.Column("id",             sa.String(36),  nullable=False),
        sa.Column("user_id",        sa.String(36),  nullable=False),
        sa.Column("filename",       sa.String(512), nullable=False),
        sa.Column("mime_type",      sa.String(127), nullable=True),
        sa.Column("status",         sa.Enum("pending", "processing", "done", "failed", name="documentstatus"),
                  nullable=False, server_default="pending"),
        sa.Column("extracted_text", sa.Text(),      nullable=True),
        sa.Column("error_message",  sa.Text(),      nullable=True),
        sa.Column("created_at",     sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at",     sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_documents_user_id", "documents", ["user_id"])

    # ── user_preferences ──────────────────────────────────────────────────
    op.create_table(
        "user_preferences",
        sa.Column("id",         sa.String(36),  nullable=False),
        sa.Column("user_id",    sa.String(36),  nullable=False),
        sa.Column("key",        sa.String(255), nullable=False),
        sa.Column("value",      sa.Text(),      nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "key", name="uq_user_preference"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_user_preferences_user_id", "user_preferences", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_user_preferences_user_id", table_name="user_preferences")
    op.drop_table("user_preferences")

    op.drop_index("ix_documents_user_id", table_name="documents")
    op.drop_table("documents")
    op.execute("DROP TYPE IF EXISTS documentstatus")

    op.drop_index("ix_chat_sessions_user_id", table_name="chat_sessions")
    op.drop_table("chat_sessions")

    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
