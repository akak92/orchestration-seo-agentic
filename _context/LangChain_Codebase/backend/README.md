# Backend — Guía de implementación

Este documento explica cómo completar cada stub del backend para exponer el `__core/` vía FastAPI.

---

## Estructura

```
backend/
├── main.py           # FastAPI app + lifespan
├── dependencies.py   # Singletons + Depends()
├── schemas.py        # Modelos Pydantic
├── routers/
│   ├── agents.py     # GET /agents  /  GET /agents/{skill_id}
│   └── chat.py       # POST /chat/{skill_id}/invoke  +  WS /chat/{skill_id}/ws
└── README.md
```

---

## 1. `dependencies.py` — Funciones de dependencia

Los singletons ya se asignan desde el `lifespan` de `main.py` vía `set_singletons()`.
Solo hay que hacer que cada `get_*` los devuelva, levantando un error claro si no están listos:

```python
def get_registry() -> AgentRegistry:
    if _registry is None:
        raise RuntimeError("Registry no inicializado.")
    return _registry

def get_sanctum() -> SanctumManager:
    if _sanctum is None:
        raise RuntimeError("Sanctum no inicializado.")
    return _sanctum

def get_llm() -> BaseChatModel:
    if _llm is None:
        raise RuntimeError("LLM no inicializado.")
    return _llm
```

Esto es todo lo que necesita este archivo. FastAPI llama automáticamente a estas funciones en cada request gracias a `Depends()`.

---

## 2. `routers/agents.py` — Listado y detalle de agentes

`AgentDescriptor` no es un modelo Pydantic, así que hay que mapear sus campos a `AgentInfo` manualmente.
Un helper interno evita repetir ese mapeo:

```python
def _to_info(d: AgentDescriptor) -> AgentInfo:
    return AgentInfo(
        skill_id        = d.skill_id,
        code            = d.code,
        name            = d.name,
        title           = d.title,
        icon            = d.icon,
        description     = d.description,
        agent_type      = d.agent_type.value,
        has_first_breath= d.has_first_breath,
        has_pulse       = d.has_pulse,
    )

@router.get("/", response_model=list[AgentInfo])
def list_agents(registry: RegistryDep):
    return [_to_info(d) for d in registry.all()]

@router.get("/{skill_id}", response_model=AgentInfo)
def get_agent(skill_id: str, registry: RegistryDep):
    d = registry.get(skill_id)
    if not d:
        raise HTTPException(status_code=404, detail=f"Agente '{skill_id}' no encontrado.")
    return _to_info(d)
```

---

## 3. `routers/chat.py` — Invoke y WebSocket

### 3.1 `POST /chat/{skill_id}/invoke`

Construye el runtime con `build_runtime()` y llama a `invoke()`:

```python
from __core.runtime import build_runtime
from pathlib import Path

WORKSPACE_DIR = str(Path(__file__).parent.parent.parent / "workspace")

@router.post("/{skill_id}/invoke", response_model=ChatResponse)
async def invoke(skill_id: str, body: ChatRequest,
                 registry: RegistryDep, sanctum: SanctumDep, llm: LLMDep):
    descriptor = registry.get(skill_id)
    if not descriptor:
        raise HTTPException(status_code=404, detail=f"Agente '{skill_id}' no encontrado.")

    runtime = build_runtime(descriptor, llm, sanctum, body.team_id, WORKSPACE_DIR)
    response = await runtime.invoke(body.message, attachments=body.attachments)

    return ChatResponse(skill_id=skill_id, team_id=body.team_id, response=response)
```

### 3.2 `WS /chat/{skill_id}/ws` — Streaming token a token

El cliente envía un JSON con `WsIncoming`, el servidor itera `runtime.stream()` y envía
un `WsChunk` por cada token. Al terminar envía `{"type": "end"}`.

```python
@router.websocket("/{skill_id}/ws")
async def stream_ws(skill_id: str, websocket: WebSocket,
                    registry: RegistryDep, sanctum: SanctumDep, llm: LLMDep):
    await websocket.accept()
    try:
        while True:
            raw      = await websocket.receive_text()
            incoming = WsIncoming.model_validate_json(raw)

            descriptor = registry.get(skill_id)
            if not descriptor:
                await websocket.send_text(
                    WsChunk(type="error", content=f"Agente '{skill_id}' no encontrado.").model_dump_json()
                )
                continue

            runtime = build_runtime(descriptor, llm, sanctum, incoming.team_id, WORKSPACE_DIR)

            try:
                async for chunk in runtime.stream(incoming.message, attachments=incoming.attachments):
                    await websocket.send_text(
                        WsChunk(type="chunk", content=chunk).model_dump_json()
                    )
                await websocket.send_text(WsChunk(type="end").model_dump_json())

            except Exception as e:
                await websocket.send_text(
                    WsChunk(type="error", content=str(e)).model_dump_json()
                )

    except WebSocketDisconnect:
        pass
```

#### Protocolo de mensajes WebSocket

| Dirección | Tipo | Cuándo |
|---|---|---|
| Cliente → Servidor | `WsIncoming` (JSON) | Al enviar un mensaje |
| Servidor → Cliente | `WsChunk { type: "chunk" }` | Por cada token generado |
| Servidor → Cliente | `WsChunk { type: "end" }` | Al terminar la respuesta |
| Servidor → Cliente | `WsChunk { type: "error" }` | Si ocurre una excepción |

---

## 4. Arrancar el servidor

```bash
# Desde 04_Codebase/
uvicorn backend.main:app --reload
```

Endpoints disponibles:

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/agents` | Lista todos los agentes registrados |
| `GET` | `/agents/{skill_id}` | Detalle de un agente |
| `POST` | `/chat/{skill_id}/invoke` | Respuesta completa (JSON) |
| `WS` | `/chat/{skill_id}/ws` | Streaming token a token |
| `GET` | `/health` | Health check |

La documentación interactiva queda disponible automáticamente en `/docs` (Swagger UI).

---

## 5. Ejemplo de cliente WebSocket (Python)

```python
import asyncio
import json
import websockets

async def chat():
    uri = "ws://localhost:8000/chat/agente-stateless/ws"
    async with websockets.connect(uri) as ws:
        await ws.send(json.dumps({"message": "¿Qué es un agente de IA?"}))

        async for raw in ws:
            chunk = json.loads(raw)
            if chunk["type"] == "chunk":
                print(chunk["content"], end="", flush=True)
            elif chunk["type"] == "end":
                print()
                break
            elif chunk["type"] == "error":
                print(f"\nError: {chunk['content']}")
                break

asyncio.run(chat())
```
