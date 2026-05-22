from app.processors.base import DocumentProcessor


class TxtProcessor(DocumentProcessor):
    async def extract_text(self, content: bytes) -> str:
        # Intentar decodificar con UTF-8; fallback a latin-1 para caracteres especiales
        try:
            return content.decode("utf-8")
        except UnicodeDecodeError:
            return content.decode("latin-1")
