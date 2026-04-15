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
