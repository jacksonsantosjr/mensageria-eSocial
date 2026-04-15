"""
Assinador XML XMLDSIG para eSocial

Assina eventos individuais e lotes completos usando certificado A1.
"""
import logging
from lxml import etree
from signxml import XMLSigner, XMLVerifier, methods

from core.exceptions import XmlSigningError

logger = logging.getLogger(__name__)


class XmlSigner:
    """Assinador XMLDSIG para eventos e lotes do eSocial."""

    def sign_event(self, event_xml: str, cert_pem: bytes, key_pem: bytes) -> str:
        """
        Assina um evento individual com XMLDSIG (assinatura enveloped).

        O elemento assinado e identificado pelo atributo Id.

        Args:
            event_xml: String XML do evento.
            cert_pem: Certificado PEM em bytes.
            key_pem: Chave privada PEM em bytes.

        Returns:
            String XML do evento assinado.

        Raises:
            XmlSigningError: Se a assinatura falhar.
        """
        try:
            root = etree.fromstring(event_xml.encode("utf-8"))
            
            signer = XMLSigner(
                method=methods.enveloped,
                signature_algorithm="rsa-sha256",
                digest_algorithm="sha256",
                c14n_algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315",
            )

            signed_root = signer.sign(
                root,
                key=key_pem,
                cert=cert_pem,
            )

            signed_xml = etree.tostring(signed_root, encoding="unicode")
            logger.debug("Evento assinado com sucesso.")
            return signed_xml

        except Exception as e:
            raise XmlSigningError(f"Falha ao assinar evento: {e}") from e

    def sign_batch(self, batch_xml: str, cert_pem: bytes, key_pem: bytes) -> str:
        """
        Assina o envelope do lote completo (segunda assinatura).

        Args:
            batch_xml: String XML do lote com eventos ja assinados.
            cert_pem: Certificado PEM em bytes.
            key_pem: Chave privada PEM em bytes.

        Returns:
            String XML do lote assinado.

        Raises:
            XmlSigningError: Se a assinatura falhar.
        """
        try:
            root = etree.fromstring(batch_xml.encode("utf-8"))
            
            signer = XMLSigner(
                method=methods.enveloped,
                signature_algorithm="rsa-sha256",
                digest_algorithm="sha256",
                c14n_algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315",
            )

            signed_root = signer.sign(
                root,
                key=key_pem,
                cert=cert_pem,
            )

            signed_xml = etree.tostring(signed_root, encoding="unicode")
            logger.info("Lote assinado com sucesso.")
            return signed_xml

        except Exception as e:
            raise XmlSigningError(f"Falha ao assinar lote: {e}") from e

    def verify_signature(self, signed_xml: str, cert_pem: bytes) -> bool:
        """
        Verifica se uma assinatura XMLDSIG existente e valida.

        Args:
            signed_xml: String XML assinado.
            cert_pem: Certificado PEM para verificacao.

        Returns:
            True se a assinatura for valida, False caso contrario.
        """
        try:
            root = etree.fromstring(signed_xml.encode("utf-8"))
            XMLVerifier().verify(root, x509_cert=cert_pem)
            logger.debug("Assinatura verificada com sucesso.")
            return True
        except Exception as e:
            logger.warning("Falha na verificacao de assinatura: %s", e)
            return False
