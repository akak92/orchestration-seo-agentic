import io

import pdfplumber

from app.processors.base import DocumentProcessor


class PdfProcessor(DocumentProcessor):
    async def extract_text(self, content: bytes) -> str:
        text_parts = []
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text.strip())
        return "\n\n".join(text_parts)
