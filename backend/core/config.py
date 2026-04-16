"""
Módulo de Configuração — eSocial Mensageria

Carrega todas as variáveis de ambiente via pydantic-settings
e disponibiliza como singleton Settings para toda a aplicação.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Configurações globais da aplicação carregadas de variáveis de ambiente."""

    # --- Banco de Dados (Supabase Postgres) ---
    database_url: str 
    
    # --- Supabase SDK / Storage ---
    supabase_url: str
    supabase_service_role_key: str
    supabase_storage_bucket: str = "xml-storage"

    # --- Ambiente ---
    environment: str = "homologacao"  # production | homologacao

    # --- Certificado Digital A1 ---
    cert_path: str = "/tmp/certs"
    cert_password: str = ""

    # --- CNPJ do Transmissor ---
    cnpj_transmissor: str = ""

    # --- CORS ---
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    # --- Modo Mock ---
    mock_esocial: bool = True

    # --- Scheduler ---
    poll_interval_seconds: int = 60
    poll_max_retries: int = 20

    @property
    def cors_origins_list(self) -> list[str]:
        """Retorna lista de origens CORS a partir da string separada por vírgula."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def is_production(self) -> bool:
        """Verifica se o ambiente é produção."""
        return self.environment.lower() == "production"

    @property
    def sqlalchemy_database_url(self) -> str:
        """
        Retorna a URL de banco adaptada para SQLAlchemy/psycopg2.
        Remove o parametro pgbouncer=true que causa erro no driver python.
        """
        url = self.database_url
        if "pgbouncer=true" in url:
            # Remove o parametro mantendo a integridade da URL
            url = url.replace("?pgbouncer=true", "")
            url = url.replace("&pgbouncer=true", "")
        return url

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()
