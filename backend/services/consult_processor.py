"""
Processador de Consultas e Recibos — eSocial Mensageria
Lógica para transformar protocolos de transmissão em recibos de entrega oficiais.
"""
import logging
import uuid
from datetime import datetime
from lxml import etree
from sqlmodel import Session, select

from db.session import engine
from db.models import Lote, Evento, EventoStatus, LoteStatus, Empresa, SystemConfig, Ambiente
from services.soap_client import ESocialSoapClient
from services.storage_service import storage_service

logger = logging.getLogger(__name__)

class ConsultProcessor:
    def __init__(self):
        self.soap_client = ESocialSoapClient()

    async def process_all_pending(self):
        """Busca no banco todos os lotes aguardando resposta e consulta o governo."""
        with Session(engine) as session:
            statement = select(Lote).where(
                Lote.status.in_([LoteStatus.SENT, LoteStatus.PROCESSING])
            )
            lotes = session.exec(statement).all()
            
            if not lotes:
                return

            logger.info("Iniciando processamento de consulta para %d lotes.", len(lotes))
            
            # Busca ambiente ativo uma vez por ciclo
            config = session.get(SystemConfig, "active_ambiente")
            ambiente_atual = config.value if config else Ambiente.HOMOLOGATION

            for lote in lotes:
                try:
                    await self.process_single_lote(lote, ambiente_atual, session)
                except Exception as e:
                    logger.error("Falha ao processar consulta do lote %s: %s", lote.id, str(e))
            
            session.commit()

    async def process_single_lote(self, lote: Lote, ambiente: str, session: Session):
        """Consulta um lote específico e atualiza seu status e eventos."""
        empresa = session.get(Empresa, lote.empresa_id)
        if not empresa or not empresa.cert_base64:
            logger.warning("Empresa %s sem certificado para consulta do lote %s", lote.empresa_id, lote.id)
            return

        # 1. Consulta via SOAP
        client = ESocialSoapClient(ambiente=ambiente)
        logger.debug("Consultando protocolo %s para lote %s", lote.protocolo, lote.id)
        
        response = client.consultar_lote(
            lote.protocolo, 
            empresa.cert_base64, 
            empresa.cert_password
        )

        if response["status"] != "SUCCESS":
            logger.error("Falha na resposta SOAP para lote %s", lote.id)
            return

        # 2. Parse do XML de Retorno
        # Nota: O eSocial retorna um envelope SOAP com o XML de retorno dentro do Body.
        # Aqui assumimos que response["xml"] já é o conteúdo XML ou precisamos extrair do envelope.
        xml_content = response["xml"]
        
        try:
            # 3. Salva XML de Retorno no Storage (Auditoria)
            storage_path = f"lotes/{lote.empresa_id}/{lote.id}_retorno.xml"
            await storage_service.upload_file(storage_path, xml_content.encode('utf-8'))
            
            # 4. Extração de Dados
            self._update_lote_from_xml(lote, xml_content, session)
            
        except Exception as e:
            logger.exception("Erro ao parsear XML de retorno do lote %s", lote.id)
            lote.erro_geral = f"Erro Parse Retorno: {str(e)}"
            session.add(lote)

    def _update_lote_from_xml(self, lote: Lote, xml_data: str, session: Session):
        """Analisa o XML de retorno e atualiza o lote e seus eventos."""
        # Remover namespaces do SOAP para facilitar XPath se necessário
        # Ou usar namespaces específicos do eSocial
        root = etree.fromstring(xml_data.encode('utf-8'))
        
        # Namespaces comuns (O eSocial muda versões, aqui usamos uma genérica para o XPath)
        ns = {
            "soap": "http://schemas.xmlsoap.org/soap/envelope/",
            "ret": "http://www.esocial.gov.br/schema/lote/eventos/envio/retornoLoteEventos/v1_1_0",
            "ev": "http://www.esocial.gov.br/schema/lote/eventos/envio/retornoEvento/v1_1_0"
        }

        # 1. Verifica Status do Lote
        # Buscamos o cdResposta dentro do status do retornoLoteEventos
        cd_resposta = root.xpath("//ret:retornoLoteEventos/ret:status/ret:cdResposta/text()", namespaces=ns)
        desc_resposta = root.xpath("//ret:retornoLoteEventos/ret:status/ret:descResposta/text()", namespaces=ns)
        
        if not cd_resposta:
            # Tentar XPath sem namespaces se falhar (fallback)
            cd_resposta = root.xpath("//*[local-name()='cdResposta']/text()")
            desc_resposta = root.xpath("//*[local-name()='descResposta']/text()")

        if not cd_resposta:
            raise Exception("Não foi possível encontrar cdResposta no XML de retorno")

        codigo = cd_resposta[0]
        logger.info("Lote %s retornou código %s: %s", lote.id, codigo, desc_resposta[0] if desc_resposta else "")

        # Códigos eSocial: 201 (Sucesso), 202 (Sucesso com Advertência)
        # 101 (Processamento em curso)
        if codigo == "101":
            lote.status = LoteStatus.PROCESSING
            lote.tentativas_consulta += 1
            session.add(lote)
            return

        # 2. Processamento Finalizado (Sucesso ou Erro)
        lote.status = LoteStatus.PROCESSED if codigo in ("201", "202") else LoteStatus.ERROR
        
        # 3. Atualiza Eventos Individuais
        # O retorno contém uma lista de <retornoEvento>
        eventos_xml = root.xpath("//*[local-name()='retornoEvento']", namespaces=ns)
        
        sucessos = 0
        erros = 0
        
        for evt_xml in eventos_xml:
            # O ID do evento está num atributo do nó pai <evento> ou similar
            # No retorno do eSocial v1.1, cada item tem o ID do evento original
            evt_id_attr = evt_xml.getparent().get("id") if evt_xml.getparent() is not None else None
            
            # Busca o evento no banco pelo ID do eSocial (ID do XML original)
            evt_db = None
            if evt_id_attr:
                statement = select(Evento).where(
                    Evento.lote_id == lote.id,
                    Evento.evento_id_esocial == evt_id_attr
                )
                evt_db = session.exec(statement).first()

            if evt_db:
                # Extrai status e recibo do evento específico
                # Nota: O conteúdo do status do evento fica "envelopado"
                evt_status_cod = evt_xml.xpath(".//*[local-name()='cdResposta']/text()")
                evt_status_desc = evt_xml.xpath(".//*[local-name()='descResposta']/text()")
                evt_recibo = evt_xml.xpath(".//*[local-name()='nrRecibo']/text()")
                
                if evt_status_cod:
                    cod = evt_status_cod[0]
                    evt_db.cd_resposta = cod
                    evt_db.desc_resposta = evt_status_desc[0] if evt_status_desc else ""
                    
                    if cod in ("201", "202") and evt_recibo:
                        evt_db.status = EventoStatus.PROCESSED
                        evt_db.nr_recibo = evt_recibo[0]
                        sucessos += 1
                    else:
                        evt_db.status = EventoStatus.ERROR
                        # Extrai ocorrências (erros detalhados)
                        ocorrencias = evt_xml.xpath(".//*[local-name()='ocorrencias']//*[local-name()='ocorrencia']")
                        oc_list = []
                        for oc in ocorrencias:
                            oc_list.append({
                                "tipo": oc.xpath(".//*[local-name()='tipo']/text()")[0] if oc.xpath(".//*[local-name()='tipo']/text()") else "",
                                "codigo": oc.xpath(".//*[local-name()='codigo']/text()")[0] if oc.xpath(".//*[local-name()='codigo']/text()") else "",
                                "descricao": oc.xpath(".//*[local-name()='descricao']/text()")[0] if oc.xpath(".//*[local-name()='descricao']/text()") else ""
                            })
                        evt_db.ocorrencias_json = {"items": oc_list}
                        erros += 1
                
                session.add(evt_db)

        # Atualiza contadores do lote
        lote.eventos_sucesso = sucessos
        lote.eventos_erro = erros
        lote.updated_at = datetime.utcnow()
        session.add(lote)

consult_processor = ConsultProcessor()
