import io

from docx import Document as DocxDocument

from app.processors.base import DocumentProcessor


class DocxProcessor(DocumentProcessor):
    async def extract_text(self, content: bytes) -> str:
        doc = DocxDocument(io.BytesIO(content))
        paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
        return "\n\n".join(paragraphs)
