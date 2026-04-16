"""Endpoints da API para o Dashboard."""
from fastapi import APIRouter, Depends
from sqlmodel import Session, select, func
from typing import List, Dict

from db.session import get_session
from db.models import Lote, LoteStatus, Ambiente
from schemas.lote import LoteResponse, DashboardResumoResponse, DashboardMetrics

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/resumo", response_model=DashboardResumoResponse)
async def get_dashboard_resumo(session: Session = Depends(get_session)):
    """Retorna estatisticas reais para os cards do Dashboard através do Pydantic."""
    
    # Buscamos todos os lotes localmente para processamento,
    # eliminando riscos de exceções nas tipagens de enum customizadas do Postgres
    todos_lotes = session.exec(select(Lote).order_by(Lote.created_at.desc())).all()
    
    total = len(todos_lotes)
    
    # Processa Enum Nativo do SQLModel diretamente no Python
    pendentes = sum(1 for l in todos_lotes if l.status in [
        LoteStatus.PENDING, LoteStatus.VALIDATING, LoteStatus.SIGNED
    ])
    processados = sum(1 for l in todos_lotes if l.status == LoteStatus.PROCESSED)
    erros = sum(1 for l in todos_lotes if l.status == LoteStatus.ERROR)
    
    recent_lotes = todos_lotes[:5] if total > 0 else []

    return DashboardResumoResponse(
        metrics=DashboardMetrics(
            total=total,
            pending=pendentes,
            processed=processados,
            errors=erros
        ),
        recent_lotes=recent_lotes
    )
