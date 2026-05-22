from app.processors.base import DocumentProcessor
from app.processors.txt_processor import TxtProcessor
from app.processors.pdf_processor import PdfProcessor
from app.processors.docx_processor import DocxProcessor
from app.processors.image_processor import ImageProcessor

_REGISTRY: dict[str, DocumentProcessor] = {
    "text/plain":    TxtProcessor(),
    "application/pdf": PdfProcessor(),
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": DocxProcessor(),
    "image/jpeg": ImageProcessor(),
    "image/png":  ImageProcessor(),
}


def get_processor(mime_type: str) -> DocumentProcessor:
    processor = _REGISTRY.get(mime_type)
    if not processor:
        raise ValueError(f"No hay procesador disponible para el tipo MIME: {mime_type}")
    return processor
