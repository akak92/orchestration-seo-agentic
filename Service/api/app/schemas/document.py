from datetime import datetime

from pydantic import BaseModel, Field

from app.models.document import DocumentStatus


class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    status: DocumentStatus


class DocumentStatusResponse(BaseModel):
    # validation_alias lee el campo 'id' del ORM pero serializa como 'document_id'
    document_id: str = Field(validation_alias="id")
    filename: str
    status: DocumentStatus
    extracted_text: str | None = None
    error_message: str | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True, "populate_by_name": True}
