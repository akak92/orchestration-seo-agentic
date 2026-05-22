import json
from pathlib import Path

import aio_pika
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.db.session import get_db
from app.models.document import Document, DocumentStatus
from app.models.user import User
from app.schemas.document import DocumentUploadResponse, DocumentStatusResponse
from app.dependencies import get_current_user

router = APIRouter()

ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
    "image/jpeg",
    "image/png",
}
MAX_FILE_SIZE_MB = 20


@router.post("/upload", response_model=DocumentUploadResponse, status_code=202)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Sube un documento al sistema. Lo persiste en la BD con estado PENDING
    y publica un job en RabbitMQ para que el worker lo procese.
    """
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=415,
            detail=f"Tipo de archivo no soportado: {file.content_type}. "
                   f"Formatos válidos: PDF, DOCX, TXT, JPEG, PNG.",
        )

    content = await file.read()
    if len(content) > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=413, detail=f"El archivo supera el límite de {MAX_FILE_SIZE_MB} MB.")

    # Persistir el documento
    doc = Document(
        user_id=current_user.id,
        filename=file.filename,
        mime_type=file.content_type,
        status=DocumentStatus.PENDING,
    )
    db.add(doc)
    await db.flush()

    # Publicar job en RabbitMQ
    try:
        connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
        async with connection:
            channel = await connection.channel()
            queue = await channel.declare_queue("document_processing", durable=True)
            message_body = json.dumps({
                "document_id": doc.id,
                "user_id":     current_user.id,
                "filename":    file.filename,
                "mime_type":   file.content_type,
                "content_b64": __import__("base64").b64encode(content).decode(),
            })
            await channel.default_exchange.publish(
                aio_pika.Message(
                    body=message_body.encode(),
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                ),
                routing_key=queue.name,
            )
    except Exception as exc:
        # Si falla la cola, el documento queda en PENDING y puede reintentarse
        raise HTTPException(status_code=502, detail=f"No se pudo encolar el documento: {exc}")

    return DocumentUploadResponse(
        document_id=doc.id,
        filename=doc.filename,
        status=doc.status,
    )


@router.get("/", response_model=list[DocumentStatusResponse])
async def list_documents(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Lista todos los documentos del usuario autenticado."""
    result = await db.execute(
        select(Document)
        .where(Document.user_id == current_user.id)
        .order_by(Document.created_at.desc())
    )
    docs = result.scalars().all()
    return [
        DocumentStatusResponse(
            id=doc.id,
            filename=doc.filename,
            status=doc.status,
            extracted_text=doc.extracted_text,
            error_message=doc.error_message,
            created_at=doc.created_at,
        )
        for doc in docs
    ]


@router.get("/{document_id}", response_model=DocumentStatusResponse)
async def get_document_status(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Consulta el estado de procesamiento de un documento."""
    result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.user_id == current_user.id,
        )
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Documento no encontrado.")

    return DocumentStatusResponse(
        id=doc.id,
        filename=doc.filename,
        status=doc.status,
        extracted_text=doc.extracted_text,
        error_message=doc.error_message,
    )
