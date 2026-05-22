import abc


class DocumentProcessor(abc.ABC):
    """Interfaz abstracta para todos los procesadores de documentos."""

    @abc.abstractmethod
    async def extract_text(self, content: bytes) -> str:
        """
        Extrae el texto del documento.

        Args:
            content: Contenido binario del archivo.

        Returns:
            Texto extraído como string plano.
        """
        ...
