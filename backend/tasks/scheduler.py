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
