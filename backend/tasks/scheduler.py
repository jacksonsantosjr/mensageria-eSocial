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

import asyncio
from services.consult_processor import consult_processor

def poll_pending_protocols():
    """
    Job periódico: Busca lotes no banco e dispara a consulta real ao eSocial.
    """
    logger.debug("Iniciando ciclo de polling de protocolos real...")
    
    # Como o APScheduler roda funções síncronas em threads, precisamos 
    # rodar o processador assíncrono dentro de um loop de evento.
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(consult_processor.process_all_pending())
        loop.close()
    except Exception as e:
        logger.error("Erro no ciclo de polling: %s", str(e))

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
