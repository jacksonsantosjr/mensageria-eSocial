import logging
import uuid
from dataclasses import dataclass, field
from typing import Optional
from core.config import settings
from core.exceptions import SoapClientError
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
        self._consult_count = {}

    def send_batch(self, signed_batch_xml: str) -> SendBatchResponse:
        if self.mock_mode:
            protocolo = f"1.0.{uuid.uuid4().hex[:20]}"
            return SendBatchResponse(protocolo=protocolo, cd_resposta="201", desc_resposta="Sucesso MOCK")
        raise SoapClientError("Modo real nao implementado (MOCK).")

    def consult_batch(self, protocol_number: str) -> ConsultBatchResponse:
        if self.mock_mode:
            cnt = self._consult_count.get(protocol_number, 0) + 1
            self._consult_count[protocol_number] = cnt
            if cnt < 2:
                return ConsultBatchResponse(cd_resposta="201", desc_resposta="Mock processando")
            return ConsultBatchResponse(cd_resposta="200", desc_resposta="Mock Sucesso", eventos=[])
        raise SoapClientError("Modo real nao implementado.")