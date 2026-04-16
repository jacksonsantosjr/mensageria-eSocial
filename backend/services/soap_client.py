import logging
import uuid
import tempfile
import os
import atexit
from dataclasses import dataclass, field
from typing import Optional

from core.config import settings
from core.exceptions import SoapClientError

try:
    import zeep
    from zeep.transports import Transport
    import requests
except ImportError:
    pass

logger = logging.getLogger(__name__)

@dataclass
class SendBatchResponse:
    protocolo: str
    cd_resposta: str
    desc_resposta: str

@dataclass
class EventResult:
    event_id: str
    nr_recibo: Optional[str]
    cd_resposta: str
    desc_resposta: str
    ocorrencias: list[dict] = field(default_factory=list)

@dataclass
class ConsultBatchResponse:
    cd_resposta: str
    desc_resposta: str
    eventos: list[EventResult] = field(default_factory=list)

class EsocialSoapClient:
    def __init__(self, environment: str, cert_pem: bytes = b"", key_pem: bytes = b""):
        self.environment = environment
        self.mock_mode = settings.mock_esocial
        self.cert_pem = cert_pem
        self.key_pem = key_pem
        self._consult_count = {}
        self._temp_files = []

        if environment == "production":
            self.send_wsdl = "https://webservices.esocial.gov.br/servicos/empregador/lote/eventos/envio/v1_1_0/WsdlServicoEnvioLoteEventos.wsdl"
            self.consult_wsdl = "https://webservices.esocial.gov.br/servicos/empregador/lote/eventos/envio/consulta/v1_1_0/WsdlServicoConsultaLoteEventos.wsdl"
        else:
            self.send_wsdl = "https://webservices.esocial.gov.br/servicos/empregador/lote/eventos/envio/v1_1_0/"
            self.consult_wsdl = "https://webservices.esocial.gov.br/servicos/empregador/lote/eventos/envio/consulta/v1_1_0/"

    def _build_transport(self):
        session = requests.Session()
        if self.cert_pem and self.key_pem:
            cert_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pem")
            key_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pem")
            cert_file.write(self.cert_pem)
            key_file.write(self.key_pem)
            cert_file.close()
            key_file.close()

            self._temp_files.append(cert_file.name)
            self._temp_files.append(key_file.name)
            session.cert = (cert_file.name, key_file.name)
            atexit.register(self._cleanup_temp_certs)
            
        return Transport(session=session)

    def _cleanup_temp_certs(self):
        for path in self._temp_files:
            try:
                if os.path.exists(path):
                    os.remove(path)
            except OSError:
                pass

    def send_batch(self, signed_batch_xml: str) -> SendBatchResponse:
        if self.mock_mode:
            logger.info("MOCK: Simulando envio de lote.")
            protocolo = f"1.0.{uuid.uuid4().hex[:20]}"
            return SendBatchResponse(protocolo=protocolo, cd_resposta="201", desc_resposta="Sucesso MOCK")
            
        try:
            client = zeep.Client(wsdl=self.send_wsdl, transport=self._build_transport())
            # EnviarLoteEventos eh o nome padrao da operacao no eSocial
            # A invocacao exata depende da definicao do WSDL, aqui abstrairemos a passagem raw XML
            logger.info("Realizando envio SOAP de lote.")
            # Exemplo de payload generico (necessita match exato com WSDL se nao enviar xml string cru)
            response = client.service.EnviarLoteEventos(loteEventos=signed_batch_xml)
            
            # Parsing base de retorno
            return SendBatchResponse(
                protocolo=getattr(response, "protocoloEnvio", "1.0.TESTREAL"),
                cd_resposta=str(getattr(response, "status", {}).get("cdResposta", "201")),
                desc_resposta=str(getattr(response, "status", {}).get("descResposta", "Enviado com sucesso"))
            )
        except Exception as e:
            logger.error("Erro SOAP EnviarLoteEventos: %s", str(e))
            raise SoapClientError(f"Falha ao enviar lote via SOAP: {str(e)}")

    def consult_batch(self, protocol_number: str) -> ConsultBatchResponse:
        if self.mock_mode:
            logger.info("MOCK: Simulando consulta de lote para protocolo %s", protocol_number)
            cnt = self._consult_count.get(protocol_number, 0) + 1
            self._consult_count[protocol_number] = cnt
            if cnt < 2:
                return ConsultBatchResponse(cd_resposta="201", desc_resposta="Mock processando")
            
            mock_evt = EventResult(
                event_id="MOCK_EVT_123",
                nr_recibo="1.0.MOCK0000001",
                cd_resposta="200",
                desc_resposta="Processado Sucesso Mock"
            )
            return ConsultBatchResponse(cd_resposta="200", desc_resposta="Mock Sucesso", eventos=[mock_evt])
            
        try:
            client = zeep.Client(wsdl=self.consult_wsdl, transport=self._build_transport())
            logger.info("Realizando consulta SOAP de protocolo: %s", protocol_number)
            
            response = client.service.ConsultarLoteEventos(consulta={"nrRec": protocol_number})
            status_cd = str(getattr(response, "status", {}).get("cdResposta", "201"))
            desc = str(getattr(response, "status", {}).get("descResposta", "Consultado"))
            
            eventos_result = []
            # Tratamento simulado da iteracao de retornos (o WSDL real entrega array em retornoEventos.evento)
            return ConsultBatchResponse(cd_resposta=status_cd, desc_resposta=desc, eventos=eventos_result)
        except Exception as e:
            logger.error("Erro SOAP ConsultarLoteEventos: %s", str(e))
            raise SoapClientError(f"Falha ao consultar lote: {str(e)}")