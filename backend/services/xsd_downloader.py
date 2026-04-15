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
