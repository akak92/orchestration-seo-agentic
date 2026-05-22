import os
from langchain_core.language_models import BaseChatModel
from langchain_openai import AzureChatOpenAI
from dotenv import load_dotenv


def build_llm() -> BaseChatModel:
    '''
    Función de fábrica para construir y configurar el modelo de lenguaje.
    Usa variables de entorno desde .env (compatible con AzureChatOpenAI).

    En la arquitectura completa del nivel 3, esta función recibe un objeto
    Settings (pydantic-settings) y soporta múltiples providers (openai,
    azure, anthropic, local/ollama). Aquí se usa la versión simplificada
    para pruebas, idéntica al patrón de 02_tutorial.
    '''
    ...
    load_dotenv()
    return AzureChatOpenAI(
        azure_endpoint=os.getenv("AZURE_ENDPOINT"),
        azure_deployment=os.getenv("AZURE_DEPLOYMENT"),
        azure_api_version=os.getenv("AZURE_API_VERSION"),
        azure_ad_token=os.getenv("AZURE_AD_TOKEN"),
        temperature=0.7,
        max_tokens=2048
    )
