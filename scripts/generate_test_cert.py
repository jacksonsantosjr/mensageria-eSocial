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
