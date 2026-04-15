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
