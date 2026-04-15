"""
Rotas de Empresas (Multi-Tenant)
CRUD de empresas do grupo empresarial.
"""
import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException, status
from schemas.empresa import EmpresaCreate, EmpresaUpdate, EmpresaResponse

router = APIRouter()

_empresas_store: dict[str, dict] = {}

@router.get("/empresas", response_model=list[EmpresaResponse])
async def listar_empresas():
    """Lista todas as empresas cadastradas."""
    return list(_empresas_store.values())

@router.post("/empresas", response_model=EmpresaResponse, status_code=status.HTTP_201_CREATED)
async def criar_empresa(empresa: EmpresaCreate):
    """Cadastra uma nova empresa."""
    for e in _empresas_store.values():
        if e["cnpj"] == empresa.cnpj:
            raise HTTPException(status_code=409, detail=f"CNPJ {empresa.cnpj} ja cadastrado.")
    empresa_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    data = {
        "id": empresa_id,
        "cnpj": empresa.cnpj,
        "razao_social": empresa.razao_social,
        "nome_fantasia": empresa.nome_fantasia,
        "ativo": True,
        "created_at": now,
        "updated_at": now,
    }
    _empresas_store[empresa_id] = data
    return data

@router.get("/empresas/{empresa_id}", response_model=EmpresaResponse)
async def obter_empresa(empresa_id: str):
    """Retorna detalhes de uma empresa."""
    emp = _empresas_store.get(empresa_id)
    if not emp:
        raise HTTPException(status_code=404, detail="Empresa nao encontrada.")
    return emp

@router.put("/empresas/{empresa_id}", response_model=EmpresaResponse)
async def atualizar_empresa(empresa_id: str, empresa: EmpresaUpdate):
    """Atualiza dados de uma empresa."""
    existing = _empresas_store.get(empresa_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Empresa nao encontrada.")
    update_data = empresa.model_dump(exclude_unset=True)
    existing.update(update_data)
    existing["updated_at"] = datetime.utcnow().isoformat()
    return existing

@router.delete("/empresas/{empresa_id}", status_code=status.HTTP_204_NO_CONTENT)
async def desativar_empresa(empresa_id: str):
    """Desativa uma empresa (soft delete)."""
    existing = _empresas_store.get(empresa_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Empresa nao encontrada.")
    existing["ativo"] = False
    existing["updated_at"] = datetime.utcnow().isoformat()
