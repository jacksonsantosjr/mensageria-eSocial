"""
Exceções de Domínio — eSocial Mensageria

Define todas as exceções específicas do sistema para garantir
tratamento de erros consistente e mensagens claras.
"""


class EsocialMensageriaError(Exception):
    """Exceção base para todas as exceções do sistema eSocial Mensageria."""
    pass


class CertificateError(EsocialMensageriaError):
    """Erro relacionado ao certificado digital A1 (carregamento, validade, formato)."""
    pass


class XmlValidationError(EsocialMensageriaError):
    """Erro de validação do XML contra o schema XSD."""

    def __init__(self, message: str, errors: list[str] | None = None):
        super().__init__(message)
        self.errors = errors or []


class XmlSigningError(EsocialMensageriaError):
    """Erro durante a assinatura digital XMLDSIG do XML."""
    pass


class SoapClientError(EsocialMensageriaError):
    """Erro de comunicação com o Web Service SOAP do eSocial."""
    pass


class BatchProcessingError(EsocialMensageriaError):
    """Erro durante o processamento de um lote de eventos."""
    pass


class XsdDownloadError(EsocialMensageriaError):
    """Erro ao baixar schemas XSD do portal do eSocial."""
    pass


class ProtocolPollingError(EsocialMensageriaError):
    """Erro durante a consulta assíncrona de protocolo."""
    pass
