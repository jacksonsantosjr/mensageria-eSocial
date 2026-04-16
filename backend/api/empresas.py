"""
Rotas de Empresas (Multi-Tenant) — Persistência Real
CRUD de empresas do grupo empresarial utilizando Supabase/PostgreSQL.
"""
import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import Session, select
from db.session import get_session
from db.models import Empresa
from schemas.empresa import EmpresaCreate, EmpresaUpdate, EmpresaResponse

router = APIRouter()

@router.get("/empresas", response_model=list[EmpresaResponse])
async def listar_empresas(session: Session = Depends(get_session)):
    """Lista todas as empresas cadastradas no banco de dados."""
    statement = select(Empresa).where(Empresa.ativo == True)
    results = session.exec(statement)
    return results.all()

@router.post("/empresas", response_model=EmpresaResponse, status_code=status.HTTP_201_CREATED)
async def criar_empresa(empresa_in: EmpresaCreate, session: Session = Depends(get_session)):
    """Cadastra uma nova empresa no Supabase."""
    # Verificar se CNPJ já existe
    statement = select(Empresa).where(Empresa.cnpj == empresa_in.cnpj)
    existing = session.exec(statement).first()
    if existing:
        raise HTTPException(status_code=409, detail=f"CNPJ {empresa_in.cnpj} já cadastrado.")
    
    db_empresa = Empresa.model_validate(empresa_in)
    session.add(db_empresa)
    session.commit()
    session.refresh(db_empresa)
    return db_empresa

@router.get("/empresas/{empresa_id}", response_model=EmpresaResponse)
async def obter_empresa(empresa_id: uuid.UUID, session: Session = Depends(get_session)):
    """Retorna detalhes de uma empresa específica."""
    emp = session.get(Empresa, empresa_id)
    if not emp:
        raise HTTPException(status_code=404, detail="Empresa não encontrada.")
    return emp

@router.put("/empresas/{empresa_id}", response_model=EmpresaResponse)
async def atualizar_empresa(empresa_id: uuid.UUID, empresa_in: EmpresaUpdate, session: Session = Depends(get_session)):
    """Atualiza dados de uma empresa."""
    db_empresa = session.get(Empresa, empresa_id)
    if not db_empresa:
        raise HTTPException(status_code=404, detail="Empresa não encontrada.")
    
    empresa_data = empresa_in.model_dump(exclude_unset=True)
    for key, value in empresa_data.items():
        setattr(db_empresa, key, value)
    
    db_empresa.updated_at = datetime.utcnow()
    session.add(db_empresa)
    session.commit()
    session.refresh(db_empresa)
    return db_empresa

@router.delete("/empresas/{empresa_id}", status_code=status.HTTP_204_NO_CONTENT)
async def desativar_empresa(empresa_id: uuid.UUID, session: Session = Depends(get_session)):
    """Desativa uma empresa (soft delete)."""
    db_empresa = session.get(Empresa, empresa_id)
    if not db_empresa:
        raise HTTPException(status_code=404, detail="Empresa não encontrada.")
    
    db_empresa.ativo = False
    db_empresa.updated_at = datetime.utcnow()
    session.add(db_empresa)
    session.commit()
    return None
