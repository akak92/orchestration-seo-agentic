from langchain_openai import AzureChatOpenAI

from app.core.config import settings


def build_llm() -> AzureChatOpenAI:
    """
    Construye el modelo AzureChatOpenAI desde variables de entorno.
    Usado por el MultiAgentOrchestrator y todos los nodos del grafo.
    """
    return AzureChatOpenAI(
        azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
        api_key=settings.AZURE_OPENAI_KEY,
        api_version=settings.AZURE_OPENAI_VERSION,
        azure_deployment=settings.AZURE_OPENAI_DEPLOYMENT,
        temperature=0.3,
        streaming=True,
    )
