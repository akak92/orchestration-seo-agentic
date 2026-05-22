import asyncio
import base64
import json
import logging

import aio_pika
import httpx

from app.processors.router import get_processor
from app.core.config import settings

logger = logging.getLogger(__name__)


async def _handle_message(message: aio_pika.IncomingMessage) -> None:
    async with message.process(requeue=False):
        try:
            body = json.loads(message.body.decode())
            document_id = body["document_id"]
            mime_type   = body["mime_type"]
            content     = base64.b64decode(body["content_b64"])

            logger.info(f"Procesando documento {document_id} ({mime_type})")

            processor = get_processor(mime_type)
            extracted_text = await processor.extract_text(content)

            await _notify_api(document_id, status="done", extracted_text=extracted_text)
            logger.info(f"Documento {document_id} procesado correctamente.")

        except Exception as exc:
            logger.error(f"Error procesando mensaje: {exc}", exc_info=True)
            document_id = body.get("document_id", "unknown")
            await _notify_api(document_id, status="failed", error_message=str(exc))


async def _notify_api(
    document_id: str,
    *,
    status: str,
    extracted_text: str | None = None,
    error_message: str | None = None,
) -> None:
    """
    Notifica al servicio API sobre el resultado del procesamiento.
    Usa un endpoint interno (worker-to-api) protegido por el service network de Docker.
    """
    payload: dict = {"status": status}
    if extracted_text is not None:
        payload["extracted_text"] = extracted_text
    if error_message is not None:
        payload["error_message"] = error_message

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            await client.patch(
                f"{settings.API_SERVICE_URL}/internal/documents/{document_id}",
                json=payload,
                headers={"X-Internal-Token": settings.INTERNAL_TOKEN},
            )
    except Exception as exc:
        logger.warning(f"No se pudo notificar a la API para doc {document_id}: {exc}")


async def start_consumer() -> None:
    connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
    async with connection:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=5)
        queue = await channel.declare_queue("document_processing", durable=True)

        logger.info("Consumer listo. Esperando mensajes...")
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                await _handle_message(message)
