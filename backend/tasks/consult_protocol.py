"""
Task de Consulta de Protocolo — Implementacao completa (Fase 3).
"""
import logging
from core.config import settings
from services.soap_client import EsocialSoapClient

logger = logging.getLogger(__name__)

async def consult_protocol_task(lote_id: str, protocol_number: str, cert_pem: bytes = b"", key_pem: bytes = b""):
    """
    Consulta resultado de um lote processado no eSocial (via background polling).
    Retorna True se finalizado (sucesso ou erro final), 
    Retorna False se ainda em processamento (201, 202).
    """
    logger.info("Executando task de consulta para lote_id=%s, protocolo=%s", lote_id, protocol_number)
    
    try:
        client = EsocialSoapClient(settings.environment, cert_pem, key_pem)
        res = client.consult_batch(protocol_number)
        
        if res.cd_resposta in ["201", "202"]:
            logger.info("Protocolo %s ainda em processamento. Aguardando proximo poll do APScheduler.", protocol_number)
            return False
            
        elif res.cd_resposta == "200":
            logger.info("Lote %s processado com sucesso pelo eSocial! (Protocolo %s).", lote_id, protocol_number)
            for evt in res.eventos:
                logger.debug("Evento ID %s - Recibo: %s - Status: %s - %s", 
                             evt.event_id, evt.nr_recibo, evt.cd_resposta, evt.desc_resposta)
                # Futuro: session.add(db) p/ cada status
            return True
            
        else:
            logger.error("Lote %s (Protocolo %s) recusado ou com erro: [%s] %s", 
                         lote_id, protocol_number, res.cd_resposta, res.desc_resposta)
            return True
            
    except Exception as e:
        logger.error("Falha ao executar consulta do lote %s na rotina do background: %s", lote_id, str(e))
        return False # Nao eh sucesso final, pode ser instabilidade de rede.
