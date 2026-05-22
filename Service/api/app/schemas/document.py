from pydantic import BaseModel

from app.models.document import DocumentStatus


class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    status: DocumentStatus


class DocumentStatusResponse(BaseModel):
    document_id: str
    filename: str
    status: DocumentStatus
    extracted_text: str | None = None
    error_message: str | None = None

    model_config = {"from_attributes": True}
