"""
Service/worker — Punto de entrada del worker de procesado de documentos.
Arranca el consumer de RabbitMQ y espera jobs indefinidamente.
"""
import asyncio
import logging

from app.queue.consumer import start_consumer

logging.basicConfig(level="INFO", format="%(asctime)s [worker] %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


async def main():
    logger.info("Worker iniciado. Esperando mensajes en la cola 'document_processing'...")
    await start_consumer()


if __name__ == "__main__":
    asyncio.run(main())
