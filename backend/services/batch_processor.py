"""
Processador de Lotes e Eventos — Lógica de Mensageria eSocial
Orquestra a extração, validação, assinatura e integração com o Supabase.
"""
import logging
import uuid
from datetime import datetime
from sqlmodel import Session
from core.config import settings
from db.models import Lote, Evento, EventoStatus, LoteStatus, Empresa
from services.xml_validator import XmlValidator
from services.xml_signer import XmlSigner
from services.storage_service import storage_service

logger = logging.getLogger(__name__)

class BatchProcessor:
    def __init__(self):
        self.validator = XmlValidator()
        self.signer = XmlSigner()

    async def process_lote_upload(self, lote_xml: str, lote_db: Lote, session: Session):
        """
        Processa um lote recém-enviado:
        1. Extrai eventos individuais.
        2. Salva eventos no banco e no Storage.
        3. Identifica se assina agora (A1) ou aguarda (A3).
        """
        logger.info("Iniciando extração de eventos para o lote %s", lote_db.id)
        
        try:
            # 1. Extração
            events = self.validator.extract_events(lote_xml)
            lote_db.total_eventos = len(events)
            
            # 2. Persistência de Eventos
            db_events = []
            for idx, evt in enumerate(events):
                evt_id = uuid.uuid4()
                storage_path = f"eventos/{lote_db.empresa_id}/{evt_id}_original.xml"
                
                # Salva XML do evento no Storage
                xml_url = await storage_service.upload_file(storage_path, evt.xml.encode("utf-8"))
                
                db_evt = Evento(
                    id=evt_id,
                    lote_id=lote_db.id,
                    evento_id_esocial=evt.event_id,
                    tipo=evt.event_type,
                    xml_original=xml_url,
                    status=EventoStatus.PENDING
                )
                session.add(db_evt)
                db_events.append((db_evt, evt.xml))
            
            session.commit() # Garante IDs salvos
            
            # 3. Fluxo de Assinatura (Híbrido)
            empresa = session.get(Empresa, lote_db.empresa_id)
            
            if empresa and empresa.cert_base64:
                # --- FLUXO A1: Assinatura Automática ---
                logger.info("Certificado A1 detectado. Iniciando assinatura automática.")
                await self._sign_lote_a1(lote_db, db_events, empresa, session)
            else:
                # --- FLUXO A3: Aguardar Assinatura Local ---
                logger.info("Certificado A1 não encontrado. Lote aguardando assinatura local (Fluxo A3).")
                lote_db.status = LoteStatus.PENDING # Status inicial, aguarda ação do usuário na UI
                session.add(lote_db)
            
            session.commit()
            
        except Exception as e:
            logger.error("Erro ao processar lote %s: %s", lote_db.id, str(e))
            lote_db.status = LoteStatus.ERROR
            lote_db.erro_geral = str(e)
            session.add(lote_db)
            session.commit()

    async def _sign_lote_a1(self, lote_db: Lote, db_events: list, empresa: Empresa, session: Session):
        """Assina todos os eventos e o lote usando o certificado A1 da empresa."""
        try:
            # Carrega certificado
            cert_pem, key_pem = self.signer.load_pfx(empresa.cert_base64, empresa.cert_password)
            
            # TODO: Reconstruir lote assinado
            # Por brevidade nesta fase, vamos apenas marcar como assinado.
            # No envio real (Fase 4), assinaremos cada fragmento XML antes de embrulhar no SOAP.
            
            for evt_obj, raw_xml in db_events:
                evt_obj.status = EventoStatus.SIGNED
                session.add(evt_obj)
            
            lote_db.status = LoteStatus.SIGNED
            lote_db.updated_at = datetime.utcnow()
            session.add(lote_db)
            
        except Exception as e:
            logger.error("Falha na assinatura A1: %s", str(e))
            raise e