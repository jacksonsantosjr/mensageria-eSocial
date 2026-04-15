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
