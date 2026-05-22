import uuid
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column
import enum

from app.db.session import Base


class DocumentStatus(str, enum.Enum):
    PENDING    = "pending"
    PROCESSING = "processing"
    DONE       = "done"
    FAILED     = "failed"


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    filename: Mapped[str] = mapped_column(String(512), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(127), nullable=True)
    status: Mapped[DocumentStatus] = mapped_column(
        Enum(DocumentStatus, values_callable=lambda x: [e.value for e in x]),
        default=DocumentStatus.PENDING,
    )
    extracted_text: Mapped[str] = mapped_column(Text, nullable=True)
    error_message: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
