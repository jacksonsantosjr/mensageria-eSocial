"""
Módulo de Gestão de Certificado Digital A1 — eSocial Mensageria

Carrega o certificado .pfx e extrai o certificado PEM e a chave privada
para uso na assinatura XMLDSIG e na autenticação mTLS com o Web Service.
"""

import logging
from pathlib import Path
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PrivateFormat,
    NoEncryption,
)
from cryptography.hazmat.primitives.serialization.pkcs12 import (
    load_key_and_certificates,
)

from core.exceptions import CertificateError

logger = logging.getLogger(__name__)


def load_certificate(pfx_path: str, password: str) -> tuple[bytes, bytes]:
    """
    Carrega um certificado A1 (.pfx) e retorna o certificado PEM e a chave privada.

    Args:
        pfx_path: Caminho para o arquivo .pfx do certificado.
        password: Senha do certificado.

    Returns:
        Tupla (cert_pem, key_pem) com os bytes do certificado e chave em formato PEM.

    Raises:
        CertificateError: Se o certificado não for encontrado, senha inválida ou formato incorreto.
    """
    path = Path(pfx_path)

    if not path.exists():
        raise CertificateError(f"Arquivo de certificado não encontrado: {pfx_path}")

    if not path.suffix.lower() in (".pfx", ".p12"):
        raise CertificateError(f"Formato de certificado inválido. Esperado .pfx ou .p12, recebido: {path.suffix}")

    try:
        pfx_data = path.read_bytes()
        password_bytes = password.encode("utf-8") if password else None

        private_key, certificate, _ = load_key_and_certificates(pfx_data, password_bytes)

        if private_key is None:
            raise CertificateError("Chave privada não encontrada no certificado .pfx")

        if certificate is None:
            raise CertificateError("Certificado não encontrado no arquivo .pfx")

        cert_pem = certificate.public_bytes(Encoding.PEM)
        key_pem = private_key.private_bytes(
            Encoding.PEM,
            PrivateFormat.PKCS8,
            NoEncryption(),
        )

        logger.info("Certificado A1 carregado com sucesso: %s", pfx_path)
        return cert_pem, key_pem

    except CertificateError:
        raise
    except ValueError as e:
        raise CertificateError(f"Senha do certificado inválida ou formato corrompido: {e}") from e
    except Exception as e:
        raise CertificateError(f"Erro ao carregar certificado: {e}") from e
