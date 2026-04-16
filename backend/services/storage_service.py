"""
Serviço de Armazenamento — eSocial Mensageria
Gerencia o upload e download de arquivos XML utilizando o Supabase Storage.
"""
import httpx
import logging
from core.config import settings

logger = logging.getLogger(__name__)

class StorageService:
    def __init__(self):
        self.url = f"{settings.supabase_url}/storage/v1"
        self.headers = {
            "Authorization": f"Bearer {settings.supabase_service_role_key}",
            "x-client-info": "supabase-python/storage-api",
        }
        self.bucket = settings.supabase_storage_bucket

    async def upload_file(self, file_path: str, content: bytes, content_type: str = "text/xml"):
        """Realiza o upload de um arquivo para o bucket do Supabase."""
        upload_url = f"{self.url}/object/{self.bucket}/{file_path}"
        
        async with httpx.AsyncClient() as client:
            # Overwrite=true para permitir re-envio se necessário
            headers = {**self.headers, "Content-Type": content_type, "x-upsert": "true"}
            response = await client.post(upload_url, content=content, headers=headers)
            
            if response.status_code != 200:
                logger.error("Erro no upload para Supabase: %s", response.text)
                raise Exception(f"Falha ao salvar arquivo no Storage: {response.status_code}")
                
            return f"{self.bucket}/{file_path}"

    def get_public_url(self, file_path: str):
        """Retorna a URL assinada ou publica do arquivo."""
        return f"{settings.supabase_url}/storage/v1/object/public/{file_path}"

storage_service = StorageService()
