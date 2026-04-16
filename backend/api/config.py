"""
API para configurações globais do sistema.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from datetime import datetime

from db.session import get_session
from db.models import SystemConfig, Ambiente

router = APIRouter()

CONFIG_KEY_AMBIENTE = "active_ambiente"

@router.get("/config")
def get_config(session: Session = Depends(get_session)):
    """Retorna o ambiente ativo no sistema."""
    config = session.get(SystemConfig, CONFIG_KEY_AMBIENTE)
    
    if not config:
        # Inicializa com Homologação se não existir
        config = SystemConfig(key=CONFIG_KEY_AMBIENTE, value=Ambiente.HOMOLOGATION)
        session.add(config)
        session.commit()
        session.refresh(config)
        
    return {"key": config.key, "value": config.value}

@router.put("/config")
def update_config(data: dict, session: Session = Depends(get_session)):
    """Atualiza o ambiente ativo."""
    new_value = data.get("value")
    if new_value not in [Ambiente.HOMOLOGATION, Ambiente.PRODUCTION]:
        raise HTTPException(status_code=400, detail="Ambiente inválido")
        
    config = session.get(SystemConfig, CONFIG_KEY_AMBIENTE)
    if not config:
        config = SystemConfig(key=CONFIG_KEY_AMBIENTE, value=new_value)
    else:
        config.value = new_value
        config.updated_at = datetime.utcnow()
        
    session.add(config)
    session.commit()
    return {"key": config.key, "value": config.value}
