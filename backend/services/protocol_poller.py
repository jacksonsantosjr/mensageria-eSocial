import logging
from core.config import settings
from services.soap_client import EsocialSoapClient
logger = logging.getLogger(__name__)

class ProtocolPoller:
    def __init__(self):
        self.client = EsocialSoapClient(environment=settings.environment)

    def poll_protocol(self, protocolo: str, attempt: int = 0):
        return self.client.consult_batch(protocolo)