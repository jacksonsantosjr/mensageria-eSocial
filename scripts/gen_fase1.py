"""
Gerador da Fase 1 — Cria todos os arquivos restantes do backend.
Execute: python scripts/gen_fase1.py
"""
import os

BASE = r"c:\Users\jackson.junior\Documents\Antigravity\Mensageria eSocial\backend"

files = {}

# ===================== API =====================

files["api/__init__.py"] = "# Modulo api\n"

files["api/health.py"] = '''\
"""
Rota de Health Check
"""
from fastapi import APIRouter
from core.config import settings

router = APIRouter()

@router.get("/health")
async def health_check():
    """Retorna status da aplicacao, versao e ambiente."""
    return {
        "status": "ok",
        "version": "1.0.0",
        "environment": settings.environment,
        "mock_mode": settings.mock_esocial,
    }
'''

files["api/empresas.py"] = '''\
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
'''

files["api/lotes.py"] = '''\
"""
Rotas de Lotes
Endpoints para upload, listagem e detalhes de lotes.
"""
import uuid
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from typing import Optional
from schemas.lote import LoteResponse, LoteDetalheResponse, DashboardResumo

router = APIRouter()

_lotes_store: dict[str, dict] = {}

@router.post("/lotes/upload", response_model=LoteResponse, status_code=201)
async def upload_lote(
    empresa_id: str = Query(..., description="ID da empresa emissora"),
    file: UploadFile = File(...),
):
    """Upload de XML de lote de eventos do eSocial."""
    if not file.filename or not file.filename.endswith(".xml"):
        raise HTTPException(status_code=400, detail="Apenas arquivos .xml sao aceitos.")
    content = await file.read()
    lote_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    data = {
        "id": lote_id, "empresa_id": empresa_id, "protocolo": None,
        "status": "PENDING", "ambiente": "HOMOLOGATION",
        "total_eventos": 0, "eventos_sucesso": 0, "eventos_erro": 0,
        "created_at": now, "updated_at": now,
    }
    _lotes_store[lote_id] = data
    return data

@router.get("/lotes", response_model=list[LoteResponse])
async def listar_lotes(
    empresa_id: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Lista lotes com paginacao e filtro por empresa."""
    lotes = list(_lotes_store.values())
    if empresa_id:
        lotes = [l for l in lotes if l["empresa_id"] == empresa_id]
    return lotes[offset:offset + limit]

@router.get("/lotes/{lote_id}", response_model=LoteDetalheResponse)
async def obter_lote(lote_id: str):
    """Retorna detalhes de um lote com eventos."""
    lote = _lotes_store.get(lote_id)
    if not lote:
        raise HTTPException(status_code=404, detail="Lote nao encontrado.")
    return {**lote, "eventos": []}

@router.post("/lotes/{lote_id}/reenviar", response_model=LoteResponse)
async def reenviar_lote(lote_id: str):
    """Re-envia um lote com status ERROR."""
    lote = _lotes_store.get(lote_id)
    if not lote:
        raise HTTPException(status_code=404, detail="Lote nao encontrado.")
    if lote["status"] != "ERROR":
        raise HTTPException(status_code=400, detail="Apenas lotes com status ERROR podem ser reenviados.")
    lote["status"] = "PENDING"
    lote["updated_at"] = datetime.utcnow().isoformat()
    return lote

@router.get("/dashboard/resumo", response_model=DashboardResumo)
async def dashboard_resumo(empresa_id: Optional[str] = Query(None)):
    """Retorna cards de resumo para o dashboard."""
    lotes = list(_lotes_store.values())
    if empresa_id:
        lotes = [l for l in lotes if l["empresa_id"] == empresa_id]
    return {
        "total": len(lotes),
        "pendentes": len([l for l in lotes if l["status"] in ("PENDING","VALIDATING","SIGNED")]),
        "enviados": len([l for l in lotes if l["status"] in ("SENT","PROCESSING")]),
        "processados": len([l for l in lotes if l["status"] == "PROCESSED"]),
        "com_erro": len([l for l in lotes if l["status"] == "ERROR"]),
    }
'''

# ===================== SCHEMAS =====================

files["schemas/__init__.py"] = "# Modulo schemas\n"

files["schemas/empresa.py"] = '''\
"""Schemas Pydantic de Empresa."""
from pydantic import BaseModel, Field
from typing import Optional

class EmpresaCreate(BaseModel):
    cnpj: str = Field(..., min_length=14, max_length=14)
    razao_social: str = Field(..., min_length=1, max_length=200)
    nome_fantasia: Optional[str] = Field(None, max_length=200)

class EmpresaUpdate(BaseModel):
    razao_social: Optional[str] = Field(None, max_length=200)
    nome_fantasia: Optional[str] = Field(None, max_length=200)
    ativo: Optional[bool] = None

class EmpresaResponse(BaseModel):
    id: str
    cnpj: str
    razao_social: str
    nome_fantasia: Optional[str] = None
    ativo: bool
    created_at: str
    updated_at: str
'''

files["schemas/lote.py"] = '''\
"""Schemas Pydantic de Lote e Evento."""
from pydantic import BaseModel
from typing import Optional

class LoteResponse(BaseModel):
    id: str
    empresa_id: str
    protocolo: Optional[str] = None
    status: str
    ambiente: str
    total_eventos: int
    eventos_sucesso: int
    eventos_erro: int
    created_at: str
    updated_at: str

class EventoResponse(BaseModel):
    id: str
    lote_id: str
    evento_id_esocial: Optional[str] = None
    tipo: Optional[str] = None
    status: str
    nr_recibo: Optional[str] = None
    cd_resposta: Optional[str] = None
    desc_resposta: Optional[str] = None
    ocorrencias_json: Optional[dict] = None
    validation_errors: Optional[dict] = None
    created_at: str
    updated_at: str

class LoteDetalheResponse(LoteResponse):
    eventos: list[EventoResponse] = []

class DashboardResumo(BaseModel):
    total: int
    pendentes: int
    enviados: int
    processados: int
    com_erro: int
'''

# ===================== TASKS =====================

files["tasks/__init__.py"] = "# Modulo tasks\n"

files["tasks/scheduler.py"] = '''\
"""
Scheduler APScheduler
Gerencia jobs assincronos para polling de protocolos pendentes.
"""
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from core.config import settings

logger = logging.getLogger(__name__)
scheduler = BackgroundScheduler()

def poll_pending_protocols():
    """Job periodico: busca lotes pendentes e consulta protocolo. Stub - Fase 3."""
    logger.debug("Polling de protocolos pendentes... (stub)")

def start_scheduler():
    """Inicia o scheduler com o job de polling."""
    scheduler.add_job(
        poll_pending_protocols, "interval",
        seconds=settings.poll_interval_seconds,
        id="poll_protocols", replace_existing=True,
    )
    scheduler.start()
    logger.info("APScheduler iniciado. Polling a cada %ds.", settings.poll_interval_seconds)

def shutdown_scheduler():
    """Encerra o scheduler."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("APScheduler encerrado.")
'''

files["tasks/consult_protocol.py"] = '''\
"""
Task de Consulta de Protocolo — Stub (Fase 3).
"""
import logging
logger = logging.getLogger(__name__)

async def consult_protocol_task(lote_id: str):
    """Consulta resultado de um lote no eSocial. Implementacao na Fase 3."""
    logger.info("consult_protocol_task para lote_id=%s (stub)", lote_id)
'''

# ===================== SERVICES =====================

files["services/__init__.py"] = "# Modulo services\n"

# ===================== TESTS =====================

files["tests/__init__.py"] = "# Modulo tests\n"

# ===================== XSD (dir vazio) =====================

files["xsd/.gitkeep"] = ""

# ===== GERAR TUDO =====
for filepath, content in files.items():
    full_path = os.path.join(BASE, filepath)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"OK: {filepath}")

print(f"\nTotal: {len(files)} arquivos criados!")
