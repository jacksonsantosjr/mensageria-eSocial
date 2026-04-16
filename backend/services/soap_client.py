"""
Cliente SOAP para comunicação mTLS com os WebServices do eSocial.
Utiliza a biblioteca cryptography para processar certificados PFX em memória.
"""
import ssl
import tempfile
import os
import base64
import requests
from lxml import etree
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.hazmat.primitives import serialization
from typing import Tuple, Optional

class ESocialSoapClient:
    # URLs de Produção Restrita (Homologação)
    URL_ENVIO_HOMOLOG = "https://webservices.producaorestrita.esocial.gov.br/servicos/empregador/enviarloteeventos/WsEnviarLoteEventos.svc"
    URL_CONSULTA_HOMOLOG = "https://webservices.producaorestrita.esocial.gov.br/servicos/empregador/consultarloteeventos/WsConsultarLoteEventos.svc"

    # URLs de Produção
    URL_ENVIO_PROD = "https://webservices.esocial.gov.br/servicos/empregador/enviarloteeventos/WsEnviarLoteEventos.svc"
    URL_CONSULTA_PROD = "https://webservices.esocial.gov.br/servicos/empregador/consultarloteeventos/WsConsultarLoteEventos.svc"

    def __init__(self, ambiente: str = "HOMOLOGATION"):
        self.ambiente = ambiente
        if ambiente == "PRODUCTION":
            self.url_envio = self.URL_ENVIO_PROD
            self.url_consulta = self.URL_CONSULTA_PROD
        else:
            self.url_envio = self.URL_ENVIO_HOMOLOG
            self.url_consulta = self.URL_CONSULTA_HOMOLOG

    def _extract_pfx(self, cert_base64: str, password: str) -> Tuple[bytes, bytes]:
        """Extrai certificado PEM e chave PEM de um PFX base64."""
        pfx_data = base64.b64decode(cert_base64)
        private_key, certificate, additional_certificates = pkcs12.load_key_and_certificates(
            pfx_data, 
            password.encode() if password else None
        )

        cert_pem = certificate.public_bytes(serialization.Encoding.PEM)
        key_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        return cert_pem, key_pem

    def enviar_lote(self, lote_xml: str, cert_base64: str, cert_pass: str) -> str:
        """Envia o lote assinado e retorna o Protocolo."""
        cert_pem, key_pem = self._extract_pfx(cert_base64, cert_pass)
        
        # O XML do lote deve ser envelopado
        # Nota: O eSocial espera o conteúdo XML do lote dentro da tag <loteEventos>
        # O conteúdo deve ser escapado ou passado como um nó.
        
        soap_envelope = f"""<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:env="http://www.esocial.gov.br/servicos/distribuicao/enviarloteeventos/v1_1_0">
   <soapenv:Header/>
   <soapenv:Body>
      <env:EnviarLoteEventos>
         <env:loteEventos>
            {lote_xml.replace('<?xml version="1.0" encoding="UTF-8"?>', '')}
         </env:loteEventos>
      </env:EnviarLoteEventos>
   </soapenv:Body>
</soapenv:Envelope>"""

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://www.esocial.gov.br/servicos/distribuicao/enviarloteeventos/v1_1_0/ServicoEnviarLoteEventos/EnviarLoteEventos"
        }

        # Cria arquivos temporários para o mTLS (o requests exige caminho de arquivo para cert/key)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".crt") as cert_file:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".key") as key_file:
                cert_file.write(cert_pem)
                key_file.write(key_pem)
                cert_path = cert_file.name
                key_path = key_file.name

        try:
            response = requests.post(
                self.url_envio, 
                data=soap_envelope.encode('utf-8'), 
                headers=headers,
                cert=(cert_path, key_path),
                timeout=30
            )
            response.raise_for_status()
            
            # Parse do Protocolo
            root = etree.fromstring(response.content)
            # Namespace do retorno
            ns = {"ns": "http://www.esocial.gov.br/servicos/distribuicao/enviarloteeventos/v1_1_0"}
            protocolo = root.xpath("//ns:protocolo/text()", namespaces=ns)
            
            if not protocolo:
                # Se não tem protocolo, pode ser erro no retorno
                error_msg = root.xpath("//ns:mensagem/text()", namespaces=ns)
                raise Exception(f"Erro eSocial: {error_msg[0] if error_msg else 'Resposta sem protocolo'}")
                
            return protocolo[0]

        finally:
            if os.path.exists(cert_path): os.remove(cert_path)
            if os.path.exists(key_path): os.remove(key_path)

    def consultar_lote(self, protocolo: str, cert_base64: str, cert_pass: str) -> dict:
        """Consulta o processamento do lote via protocolo."""
        cert_pem, key_pem = self._extract_pfx(cert_base64, cert_pass)
        
        soap_envelope = f"""<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:cons="http://www.esocial.gov.br/servicos/distribuicao/consultarloteeventos/v1_1_0">
   <soapenv:Header/>
   <soapenv:Body>
      <cons:ConsultarLoteEventos>
         <cons:consulta>
            <cons:protocolo>{protocolo}</cons:protocolo>
         </cons:consulta>
      </cons:ConsultarLoteEventos>
   </soapenv:Body>
</soapenv:Envelope>"""

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://www.esocial.gov.br/servicos/distribuicao/consultarloteeventos/v1_1_0/ServicoConsultarLoteEventos/ConsultarLoteEventos"
        }

        with tempfile.NamedTemporaryFile(delete=False, suffix=".crt") as cert_file:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".key") as key_file:
                cert_file.write(cert_pem)
                key_file.write(key_pem)
                cert_path = cert_file.name
                key_path = key_file.name

        try:
            response = requests.post(
                self.url_consulta, 
                data=soap_envelope.encode('utf-8'), 
                headers=headers,
                cert=(cert_path, key_path),
                timeout=30
            )
            response.raise_for_status()
            return {"status": "SUCCESS", "xml": response.text}
        finally:
            if os.path.exists(cert_path): os.remove(cert_path)
            if os.path.exists(key_path): os.remove(key_path)