import logging
from dataclasses import dataclass
from core.config import settings
from services.xml_validator import XmlValidator
from services.xml_signer import XmlSigner
from services.soap_client import EsocialSoapClient
logger = logging.getLogger(__name__)
	@dataclass
class ProcessResult:
    lote_id: str
    total_eventos: int
    eventos_validos: int
    eventos_invalidos: int
    validation_details: list[dict]

class BatchProcessor:
    def __init__(self):
        self.validator = XmlValidator()
        self.signer = XmlSigner()

    def process_upload(self, lote_xml: str, lote_id: str) -> ProcessResult:
        events = self.validator.extract_events(lote_xml)
        return ProcessResult(lote_id, len(events), len(events), 0, [])

    def send__to_esocial(self, lote_xml: str, lote_id: str) -> str:
        client = EsocialSoapClient(settings.environment)
        res = client.send_batch(lote_xml)
        return res.protocolo