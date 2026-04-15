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
