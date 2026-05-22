import json
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from backend.dependencies import RegistryDep, SanctumDep, LLMDep
from backend.schemas import ChatRequest, ChatResponse, WsIncoming, WsChunk

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/{skill_id}/invoke", response_model=ChatResponse)
async def invoke(
    skill_id: str,
    body: ChatRequest,
    registry: RegistryDep,
    sanctum: SanctumDep,
    llm: LLMDep,
):
    '''
    Llama a runtime.invoke() y devuelve la respuesta completa.
    Adecuado para clientes que no necesitan streaming.
    '''
    ...


@router.websocket("/{skill_id}/ws")
async def stream_ws(
    skill_id: str,
    websocket: WebSocket,
    registry: RegistryDep,
    sanctum: SanctumDep,
    llm: LLMDep,
):
    '''
    WebSocket para streaming token a token vía runtime.stream().

    Protocolo:
        Cliente → servidor: WsIncoming (JSON)
        Servidor → cliente: WsChunk   (JSON, tipo "chunk") por cada token
                            WsChunk   (JSON, tipo "end")   al finalizar
                            WsChunk   (JSON, tipo "error") si hay excepción

    La conexión permanece abierta: el cliente puede enviar múltiples mensajes
    de forma secuencial dentro de la misma sesión WebSocket.
    '''
    await websocket.accept()
    try:
        while True:
            raw = await websocket.receive_text()
            incoming = WsIncoming.model_validate_json(raw)

            # TODO: construir runtime, iterar stream() y enviar chunks
            ...

    except WebSocketDisconnect:
        pass
