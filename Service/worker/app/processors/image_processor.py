import io

import pytesseract
from PIL import Image

from app.processors.base import DocumentProcessor


class ImageProcessor(DocumentProcessor):
    """
    Extrae texto de imágenes (JPEG, PNG) usando Tesseract OCR.
    Requiere que Tesseract esté instalado en el sistema operativo del contenedor.
    """

    async def extract_text(self, content: bytes) -> str:
        image = Image.open(io.BytesIO(content))
        # lang='spa+eng' para soportar textos en español e inglés
        text = pytesseract.image_to_string(image, lang="spa+eng")
        return text.strip()
