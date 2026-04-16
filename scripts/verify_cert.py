import os
import base64
import logging
from pathlib import Path
from dotenv import load_dotenv
import sys

# Adiciona o diretorio backend ao path para importar os servicos
sys.path.append(os.path.join(os.getcwd(), "backend"))

from services.xml_signer import XmlSigner

# Configuração de Logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_certificate_loading():
    load_dotenv()
    
    cert_path_dir = os.getenv("CERT_PATH")
    cert_password = os.getenv("CERT_PASSWORD")
    
    if not cert_path_dir or not os.path.exists(cert_path_dir):
        logger.error(f"Diretorio de certificados nao encontrado: {cert_path_dir}")
        return

    # Procurar por arquivos .pfx no diretorio
    pfx_files = list(Path(cert_path_dir).glob("*.pfx"))
    
    if not pfx_files:
        logger.error("Nenhum arquivo .pfx encontrado no diretorio configurado.")
        return
    
    pfx_file = pfx_files[0]
    logger.info(f"Testando certificado: {pfx_file.name}")
    
    with open(pfx_file, "rb") as f:
        pfx_data = f.read()
        pfx_base64 = base64.b64encode(pfx_data).decode("utf-8")
    
    signer = XmlSigner()
    
    try:
        cert_pem, key_pem = signer.load_pfx(pfx_base64, cert_password)
        logger.info("✅ SUCESSO: Certificado e chave privada carregados corretamente!")
        
        # Testar uma assinatura simples
        test_xml = "<root Id='ID123'><data>Teste de Assinatura</data></root>"
        signed_xml = signer.sign_event(test_xml, cert_pem, key_pem)
        
        if "<Signature" in signed_xml:
            logger.info("✅ SUCESSO: Assinatura XML gerada com sucesso!")
            
            # Verificar
            is_valid = signer.verify_signature(signed_xml, cert_pem)
            if is_valid:
                logger.info("✅ SUCESSO: Assinatura validada com sucesso!")
            else:
                logger.error("❌ FALHA: Assinatura gerada e invalida.")
        else:
            logger.error(f"❌ FALHA: Tag Signature nao encontrada no XML gerado. XML result: {signed_xml}")
            
    except Exception as e:
        logger.error(f"❌ ERRO durante o teste: {e}")

if __name__ == "__main__":
    test_certificate_loading()
