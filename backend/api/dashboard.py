"""Endpoints da API para o Dashboard."""
from fastapi import APIRouter, Depends
from sqlmodel import Session, select, func
from typing import List, Dict

from db.session import get_session
from db.models import Lote, LoteStatus, Ambiente
from schemas.lote import LoteResponse

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/resumo")
async def get_dashboard_resumo(session: Session = Depends(get_session)):
    """Retorna estatisticas reais para os cards do Dashboard."""
    
    # 1. Total Lotes
    total_lotes = session.exec(select(func.count(Lote.id))).first() or 0
    
    # 2. Pendentes (PENDING, VALIDATING, SIGNED)
    pendentes_query = select(func.count(Lote.id)).where(Lote.status.in_([
        LoteStatus.PENDING.value, 
        LoteStatus.VALIDATING.value, 
        LoteStatus.SIGNED.value
    ]))
    pendentes = session.exec(pendentes_query).first() or 0
    
    # 3. Processados (PROCESSED)
    processados = session.exec(
        select(func.count(Lote.id)).where(Lote.status == LoteStatus.PROCESSED)
    ).first() or 0
    
    # 4. Rejeitados / Erro (ERROR + SENT/PROCESSING que falharam)
    erros = session.exec(
        select(func.count(Lote.id)).where(Lote.status == LoteStatus.ERROR)
    ).first() or 0

    # 5. Ultimos 5 Lotes
    statement = select(Lote).order_by(Lote.created_at.desc()).limit(5)
    recent_lotes = session.exec(statement).all()

    return {
        "metrics": {
            "total": total_lotes,
            "pending": pendentes,
            "processed": processados,
            "errors": erros
        },
        "recent_lotes": [LoteResponse.model_validate(l).model_dump(mode="json") for l in recent_lotes]
    }
