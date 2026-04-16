"""
Scheduler APScheduler — Polling Real
Gerencia jobs assíncronos para consulta automática de protocolos no eSocial.
"""
import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from sqlmodel import Session, select
from core.config import settings
from db.session import engine
from db.models import Lote, LoteStatus

logger = logging.getLogger(__name__)
scheduler = BackgroundScheduler()

def poll_pending_protocols():
    """
    Job periódico: Busca lotes no Supabase com status de transmissão pendente
    e dispara a consulta ao Web Service do eSocial.
    """
    logger.debug("Iniciando ciclo de polling de protocolos...")
    
    with Session(engine) as session:
        # Busca lotes que foram enviados mas ainda não processados totalmente
        statement = select(Lote).where(
            Lote.status.in_([LoteStatus.SENT, LoteStatus.PROCESSING])
        )
        lotes_pendentes = session.exec(statement).all()
        
        if not lotes_pendentes:
            return

        logger.info("Encontrados %d lotes para consulta de protocolo.", len(lotes_pendentes))
        
        for lote in lotes_pendentes:
            try:
                # Aqui entrará a chamada real ao SOAP client na Fase 4
                # Por enquanto, logamos a intenção de consulta
                logger.debug("Consultando protocolo %s para o lote %s", lote.protocolo, lote.id)
                
                # Mock de incremento de tentativas
                lote.tentativas_consulta += 1
                lote.updated_at = datetime.utcnow()
                session.add(lote)
                
            except Exception as e:
                logger.error("Erro ao consultar lote %s: %s", lote.id, str(e))
        
        session.commit()

def start_scheduler():
    """Inicia o scheduler com o job de polling configurado."""
    # Evita adicionar múltiplos jobs se o scheduler já estiver rodando
    if not scheduler.get_job("poll_protocols"):
        scheduler.add_job(
            poll_pending_protocols, "interval",
            seconds=settings.poll_interval_seconds,
            id="poll_protocols", replace_existing=True,
        )
    
    if not scheduler.running:
        scheduler.start()
        logger.info("APScheduler iniciado. Monitorando protocolos no Supabase a cada %ds.", settings.poll_interval_seconds)

def shutdown_scheduler():
    """Encerra o scheduler de forma segura."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("APScheduler encerrado.")
