from fastapi import APIRouter, HTTPException
from backend.dependencies import RegistryDep
from backend.schemas import AgentInfo

router = APIRouter(prefix="/agents", tags=["agents"])


@router.get("/", response_model=list[AgentInfo])
def list_agents(registry: RegistryDep):
    '''Devuelve todos los agentes registrados.'''
    ...


@router.get("/{skill_id}", response_model=AgentInfo)
def get_agent(skill_id: str, registry: RegistryDep):
    '''Devuelve el descriptor de un agente por su skill_id.'''
    ...
