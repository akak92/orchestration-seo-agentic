"""
Router interno — solo accesible dentro de la red Docker.
Usado por el worker para actualizar el estado de los documentos procesados.
"""
from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.db.session import get_db
from app.models.document import Document, DocumentStatus

router = APIRouter()


class DocumentResultPayload(BaseModel):
    status:         str
    extracted_text: str | None = None
    error_message:  str | None = None


def _verify_internal_token(x_internal_token: str = Header(...)):
    if x_internal_token != settings.INTERNAL_TOKEN:
        raise HTTPException(status_code=403, detail="Token interno inválido.")


@router.patch("/documents/{document_id}")
async def update_document_result(
    document_id: str,
    payload: DocumentResultPayload,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(_verify_internal_token),
):
    result = await db.execute(select(Document).where(Document.id == document_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Documento no encontrado.")

    doc.status = DocumentStatus(payload.status)
    if payload.extracted_text is not None:
        doc.extracted_text = payload.extracted_text
    if payload.error_message is not None:
        doc.error_message = payload.error_message

    db.add(doc)
    return {"ok": True}
