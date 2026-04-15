"""
Gerador da Fase 2 — Validador XML, Assinador XML, Download XSD e testes.
Execute: python scripts/gen_fase2.py
"""
import os

BASE = r"c:\Users\jackson.junior\Documents\Antigravity\Mensageria eSocial\backend"
SCRIPTS = r"c:\Users\jackson.junior\Documents\Antigravity\Mensageria eSocial\scripts"

files = {}

# ===== services/xsd_downloader.py =====
files["services/xsd_downloader.py"] = '''\
"""
Downloader de Schemas XSD do eSocial

Baixa automaticamente os schemas XSD do portal do eSocial,
mantendo cache local no diretorio /xsd/.
"""
import logging
import os
from pathlib import Path
from typing import Optional

import httpx

from core.config import settings
from core.exceptions import XsdDownloadError

logger = logging.getLogger(__name__)

# URL base dos schemas XSD do eSocial S-1.3
XSD_BASE_URL = "https://www.gov.br/esocial/pt-br/documentacao-tecnica/leiautes-702-702-01-e-s-1-3/schemas-xsd-s-1-3.zip"

# Diretorio de cache local
XSD_CACHE_DIR = Path(os.path.dirname(os.path.dirname(__file__))) / "xsd"


class XsdDownloader:
    """Gerencia download e cache de schemas XSD do eSocial."""

    def __init__(self, cache_dir: Optional[Path] = None):
        self.cache_dir = cache_dir or XSD_CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get_xsd_path(self, event_type: str) -> Path:
        """
        Retorna o caminho do arquivo XSD para o tipo de evento.

        Args:
            event_type: Tipo do evento (ex: "S-2200", "evtAdmissao")

        Returns:
            Path para o arquivo XSD correspondente.

        Raises:
            XsdDownloadError: Se o schema nao for encontrado no cache.
        """
        # Normalizar nome do evento
        normalized = event_type.replace("-", "").replace("_", "").lower()
        
        # Buscar XSD no cache
        for xsd_file in self.cache_dir.glob("*.xsd"):
            if normalized in xsd_file.name.lower():
                return xsd_file
        
        raise XsdDownloadError(
            f"Schema XSD nao encontrado para o tipo '{event_type}'. "
            f"Execute a atualizacao dos schemas via POST /api/xsd/atualizar."
        )

    async def download_schemas(self) -> dict:
        """
        Baixa o pacote de schemas XSD do portal do eSocial.

        Returns:
            Dict com status do download (arquivos baixados, versao, etc.)

        Raises:
            XsdDownloadError: Se o download falhar.
        """
        try:
            logger.info("Iniciando download dos schemas XSD do eSocial...")
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.get(XSD_BASE_URL, follow_redirects=True)
                response.raise_for_status()

            # Salvar o ZIP e extrair
            import zipfile
            import io
            
            zip_data = io.BytesIO(response.content)
            
            with zipfile.ZipFile(zip_data, "r") as zf:
                xsd_files = [f for f in zf.namelist() if f.endswith(".xsd")]
                for xsd_file in xsd_files:
                    filename = os.path.basename(xsd_file)
                    target_path = self.cache_dir / filename
                    with open(target_path, "wb") as out_file:
                        out_file.write(zf.read(xsd_file))
                
                logger.info("Download concluido: %d schemas XSD extraidos.", len(xsd_files))
                
                return {
                    "status": "success",
                    "schemas_count": len(xsd_files),
                    "files": [os.path.basename(f) for f in xsd_files],
                }

        except httpx.HTTPError as e:
            raise XsdDownloadError(f"Falha no download dos schemas XSD: {e}") from e
        except zipfile.BadZipFile as e:
            raise XsdDownloadError(f"Arquivo ZIP dos schemas esta corrompido: {e}") from e
        except Exception as e:
            raise XsdDownloadError(f"Erro inesperado ao baixar schemas: {e}") from e

    def list_cached_schemas(self) -> list[str]:
        """Lista os schemas XSD disponiveis no cache local."""
        return sorted([f.name for f in self.cache_dir.glob("*.xsd")])

    def has_cached_schemas(self) -> bool:
        """Verifica se ha schemas no cache local."""
        return len(list(self.cache_dir.glob("*.xsd"))) > 0
'''

# ===== services/xml_validator.py =====
files["services/xml_validator.py"] = '''\
"""
Validador XML contra schemas XSD do eSocial

Valida eventos individuais e extrai eventos de lotes.
"""
import logging
from dataclasses import dataclass, field
from typing import Optional

from lxml import etree

from core.exceptions import XmlValidationError
from services.xsd_downloader import XsdDownloader

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Resultado da validacao de um XML contra XSD."""
    is_valid: bool
    errors: list[str] = field(default_factory=list)


@dataclass
class EventXml:
    """Evento individual extraido de um lote."""
    event_id: str
    event_type: str
    xml: str


class XmlValidator:
    """Validador de XMLs de eventos do eSocial contra schemas XSD."""

    def __init__(self, xsd_downloader: Optional[XsdDownloader] = None):
        self.xsd_downloader = xsd_downloader or XsdDownloader()

    def validate_against_xsd(self, xml_string: str, event_type: str) -> ValidationResult:
        """
        Valida um XML de evento contra o schema XSD correspondente.

        Args:
            xml_string: String XML do evento.
            event_type: Tipo do evento (ex: "S-2200").

        Returns:
            ValidationResult com is_valid e lista de erros.
        """
        try:
            xsd_path = self.xsd_downloader.get_xsd_path(event_type)
            
            with open(xsd_path, "rb") as xsd_file:
                xsd_doc = etree.parse(xsd_file)
                xsd_schema = etree.XMLSchema(xsd_doc)

            xml_doc = etree.fromstring(xml_string.encode("utf-8"))
            
            if xsd_schema.validate(xml_doc):
                return ValidationResult(is_valid=True)
            else:
                errors = [str(err) for err in xsd_schema.error_log]
                return ValidationResult(is_valid=False, errors=errors)

        except XmlValidationError:
            raise
        except etree.XMLSyntaxError as e:
            return ValidationResult(is_valid=False, errors=[f"XML mal formado: {e}"])
        except Exception as e:
            return ValidationResult(is_valid=False, errors=[f"Erro de validacao: {e}"])

    def extract_events(self, lote_xml: str) -> list[EventXml]:
        """
        Extrai eventos individuais de um XML de lote.

        Args:
            lote_xml: String XML do lote completo.

        Returns:
            Lista de EventXml com id, tipo e xml de cada evento.

        Raises:
            XmlValidationError: Se o XML nao possuir estrutura de lote valida.
        """
        try:
            root = etree.fromstring(lote_xml.encode("utf-8"))
        except etree.XMLSyntaxError as e:
            raise XmlValidationError(f"XML mal formado: {e}")

        # Buscar elementos <evento> em qualquer namespace
        eventos = root.findall(".//{*}evento")
        
        if not eventos:
            # Tentar sem namespace
            eventos = root.findall(".//evento")
        
        if not eventos:
            raise XmlValidationError(
                "XML nao possui estrutura de lote eSocial valida. "
                "Nenhum elemento <evento> encontrado."
            )

        result = []
        for evento in eventos:
            event_id = evento.get("Id", evento.get("id", ""))
            
            # Extrair o XML interno do evento
            inner_elements = list(evento)
            if inner_elements:
                event_xml = etree.tostring(inner_elements[0], encoding="unicode")
                event_type = self.detect_event_type(event_xml)
            else:
                event_xml = etree.tostring(evento, encoding="unicode")
                event_type = self.detect_event_type(event_xml)

            result.append(EventXml(
                event_id=event_id,
                event_type=event_type,
                xml=event_xml,
            ))

        logger.info("Extraidos %d eventos do lote.", len(result))
        return result

    def detect_event_type(self, event_xml: str) -> str:
        """
        Detecta o tipo do evento (S-2200, S-2300, etc.) pelo namespace ou tag raiz.

        Args:
            event_xml: String XML do evento individual.

        Returns:
            Tipo do evento como string (ex: "S-2200").
        """
        try:
            root = etree.fromstring(event_xml.encode("utf-8") if isinstance(event_xml, str) else event_xml)
            tag = root.tag
            
            # Remover namespace se presente
            if "}" in tag:
                tag = tag.split("}")[1]
            
            # Mapear tags conhecidas para tipos de evento
            tag_map = {
                "evtInfoEmpregador": "S-1000",
                "evtTabEstab": "S-1005",
                "evtTabRubrica": "S-1010",
                "evtTabLotacao": "S-1020",
                "evtTabCargo": "S-1030",
                "evtTabCarreira": "S-1035",
                "evtTabFuncao": "S-1040",
                "evtTabHorContratual": "S-1050",
                "evtTabAmbiente": "S-1060",
                "evtTabProcesso": "S-1070",
                "evtTabOperPort": "S-1080",
                "evtRemun": "S-1200",
                "evtRmnRPPS": "S-1202",
                "evtBenPrRP": "S-1207",
                "evtPgtos": "S-1210",
                "evtTotalContrib": "S-1299",
                "evtReabreEvPer": "S-1298",
                "evtAdmissao": "S-2200",
                "evtAltCadastral": "S-2205",
                "evtAltContratual": "S-2206",
                "evtCAT": "S-2210",
                "evtAfastTemp": "S-2230",
                "evtDeslig": "S-2299",
                "evtTSVInicio": "S-2300",
                "evtTSVAltContr": "S-2306",
                "evtTSVTermino": "S-2399",
                "evtCdBenPrRP": "S-2400",
                "evtCdBenAlt": "S-2405",
                "evtCdBenTerm": "S-2410",
                "evtExclusao": "S-3000",
                "evtFechaEvPer": "S-1299",
            }
            
            return tag_map.get(tag, f"DESCONHECIDO ({tag})")

        except Exception:
            return "DESCONHECIDO"
'''

# ===== services/xml_signer.py =====
files["services/xml_signer.py"] = '''\
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
'''

# ===== tests/test_xml_validator.py =====
files["tests/test_xml_validator.py"] = '''\
"""Testes unitarios para o XmlValidator."""
import pytest
from services.xml_validator import XmlValidator, ValidationResult

validator = XmlValidator()

SAMPLE_LOTE_XML = """<?xml version="1.0" encoding="UTF-8"?>
<eSocial xmlns="http://www.esocial.gov.br/schema/lote/eventos/envio/v1_1_0">
  <envioLoteEventos grupo="1">
    <ideEmpregador>
      <tpInsc>1</tpInsc>
      <nrInsc>12345678000100</nrInsc>
    </ideEmpregador>
    <ideTransmissor>
      <tpInsc>1</tpInsc>
      <nrInsc>12345678000100</nrInsc>
    </ideTransmissor>
    <eventos>
      <evento Id="ID1234567890123456789012345678901234567890">
        <evtAdmissao>
          <ideEvento>
            <tpAmb>2</tpAmb>
          </ideEvento>
        </evtAdmissao>
      </evento>
    </eventos>
  </envioLoteEventos>
</eSocial>"""


def test_extract_events_from_lote():
    """Testa extracao de eventos de um lote XML."""
    events = validator.extract_events(SAMPLE_LOTE_XML)
    assert len(events) >= 1
    assert events[0].event_id != ""


def test_detect_event_type_admissao():
    """Testa deteccao do tipo de evento S-2200 (admissao)."""
    xml = "<evtAdmissao><ideEvento/></evtAdmissao>"
    result = validator.detect_event_type(xml)
    assert result == "S-2200"


def test_detect_event_type_desligamento():
    """Testa deteccao do tipo de evento S-2299 (desligamento)."""
    xml = "<evtDeslig><ideEvento/></evtDeslig>"
    result = validator.detect_event_type(xml)
    assert result == "S-2299"


def test_detect_event_type_unknown():
    """Testa deteccao de evento desconhecido."""
    xml = "<evtCustom><data/></evtCustom>"
    result = validator.detect_event_type(xml)
    assert "DESCONHECIDO" in result


def test_extract_events_invalid_xml():
    """Testa que XML invalido gera erro."""
    with pytest.raises(Exception):
        validator.extract_events("isso nao e xml")


def test_extract_events_no_eventos():
    """Testa que XML sem eventos gera erro."""
    with pytest.raises(Exception):
        validator.extract_events("<root><nothing/></root>")
'''

# ===== tests/test_xml_signer.py =====
files["tests/test_xml_signer.py"] = '''\
"""Testes unitarios para o XmlSigner."""
import pytest
import subprocess
import tempfile
import os
from services.xml_signer import XmlSigner

signer = XmlSigner()


def generate_test_cert():
    """Gera certificado autoassinado para testes."""
    from cryptography import x509
    from cryptography.x509.oid import NameOID
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    import datetime

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, "Test eSocial Cert"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Test Org"),
        x509.NameAttribute(NameOID.COUNTRY_NAME, "BR"),
    ])
    
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.utcnow())
        .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=365))
        .sign(key, hashes.SHA256())
    )

    cert_pem = cert.public_bytes(serialization.Encoding.PEM)
    key_pem = key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    return cert_pem, key_pem


SAMPLE_XML = """<?xml version="1.0" encoding="UTF-8"?>
<evtAdmissao Id="ID1234567890">
  <ideEvento>
    <tpAmb>2</tpAmb>
  </ideEvento>
</evtAdmissao>"""


def test_sign_event():
    """Testa assinatura de evento individual."""
    cert_pem, key_pem = generate_test_cert()
    signed = signer.sign_event(SAMPLE_XML, cert_pem, key_pem)
    assert "<Signature" in signed or "SignatureValue" in signed


def test_sign_and_verify():
    """Testa assinatura e verificacao."""
    cert_pem, key_pem = generate_test_cert()
    signed = signer.sign_event(SAMPLE_XML, cert_pem, key_pem)
    is_valid = signer.verify_signature(signed, cert_pem)
    assert is_valid is True


def test_verify_invalid_signature():
    """Testa que assinatura corrompida falha na verificacao."""
    cert_pem, key_pem = generate_test_cert()
    signed = signer.sign_event(SAMPLE_XML, cert_pem, key_pem)
    # Corromper a assinatura
    corrupted = signed.replace("SignatureValue>", "SignatureValue>AAAA", 1)
    # Pode retornar False ou lancar excecao
    result = signer.verify_signature(corrupted, cert_pem)
    # Se nao lancou excecao, deve ser False
    assert result is False
'''

# ===== scripts/generate_test_cert.py =====
scripts_files = {}
scripts_files["generate_test_cert.py"] = '''\
"""
Gerador de Certificado de Teste (Autoassinado)

Gera um certificado .pfx autoassinado para uso em
testes locais e homologacao, sem depender de certificado real.

Uso: python scripts/generate_test_cert.py
"""
import datetime
from pathlib import Path
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization.pkcs12 import serialize_key_and_certificates


def generate_test_certificate(
    output_dir: str = "./certs",
    password: str = "test123",
    cn: str = "eSocial Mensageria - Certificado de Teste",
) -> str:
    """
    Gera um certificado autoassinado .pfx.

    Args:
        output_dir: Diretorio de saida.
        password: Senha do certificado.
        cn: Common Name do certificado.

    Returns:
        Caminho do arquivo .pfx gerado.
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Gerar chave privada RSA 2048
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    # Gerar certificado autoassinado
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, cn),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Antigravity Platform"),
        x509.NameAttribute(NameOID.COUNTRY_NAME, "BR"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "SP"),
    ])

    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.utcnow())
        .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=365))
        .sign(key, hashes.SHA256())
    )

    # Gerar .pfx
    pfx_data = serialize_key_and_certificates(
        name=b"esocial-test",
        key=key,
        cert=cert,
        cas=None,
        encryption_algorithm=serialization.BestAvailableEncryption(password.encode()),
    )

    pfx_path = output_path / "test_certificate.pfx"
    pfx_path.write_bytes(pfx_data)

    # Gerar tambem PEM separados (util para debug)
    cert_pem_path = output_path / "test_certificate.pem"
    key_pem_path = output_path / "test_key.pem"

    cert_pem_path.write_bytes(cert.public_bytes(serialization.Encoding.PEM))
    key_pem_path.write_bytes(
        key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        )
    )

    print(f"Certificado de teste gerado com sucesso!")
    print(f"  PFX: {pfx_path}")
    print(f"  PEM: {cert_pem_path}")
    print(f"  Key: {key_pem_path}")
    print(f"  Senha: {password}")
    return str(pfx_path)


if __name__ == "__main__":
    generate_test_certificate()
'''

# ===== GERAR TUDO - Backend =====
for filepath, content in files.items():
    full_path = os.path.join(BASE, filepath)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"OK: backend/{filepath}")

# ===== GERAR TUDO - Scripts =====
for filepath, content in scripts_files.items():
    full_path = os.path.join(SCRIPTS, filepath)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"OK: scripts/{filepath}")

print(f"\nTotal: {len(files) + len(scripts_files)} arquivos criados!")
