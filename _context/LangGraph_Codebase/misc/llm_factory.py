"""
misc/llm_factory.py — Fábrica del modelo de lenguaje.

RESPONSABILIDAD:
    Construir y configurar el LLM a partir de variables de entorno.
    Punto único de configuración del modelo para todo el proyecto.

CUÁNDO MODIFICAR:
    - Al cambiar de proveedor (Azure → OpenAI, Anthropic, Ollama…).
    - Al añadir parámetros de configuración (temperatura, max_tokens…).
    - Al añadir soporte para múltiples modelos (ej. uno para el Supervisor
      y otro más ligero para los agentes simples).

CONSEJOS:
    - Carga las variables con load_dotenv() al inicio. El archivo .env
      debe estar en la raíz del proyecto o en la carpeta del tutorial.
    - No hardcodees credenciales aquí. Usa siempre os.getenv().
    - La firma devuelve BaseChatModel para que el resto del código sea
      agnóstico al proveedor concreto.
    - Para tests unitarios, puedes devolver un FakeListChatModel de
      langchain_core en lugar del modelo real.
"""

import os
from langchain_core.language_models import BaseChatModel
from dotenv import load_dotenv


def build_llm() -> BaseChatModel:
    """
    Construye el modelo de lenguaje desde variables de entorno.

    Variables esperadas en .env:
        AZURE_OPENAI_ENDPOINT   : URL del endpoint de Azure OpenAI.
        AZURE_OPENAI_DEPLOYMENT : Nombre del deployment del modelo.
        AZURE_OPENAI_KEY        : API key de Azure OpenAI.
        AZURE_OPENAI_VERSION    : Versión de la API (ej. "2024-02-01").

    Returns:
        Instancia de BaseChatModel lista para usar.
    """
    load_dotenv()
    ...  # TODO: construir y devolver el LLM con las variables de entorno
