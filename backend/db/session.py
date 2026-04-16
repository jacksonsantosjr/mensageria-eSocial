"""
Gerenciamento de Sessão de Banco de Dados — eSocial Mensageria

Utiliza SQLModel para criar a engine e gerenciar o ciclo de vida
das sessões de banco de dados (Dependency Injection).
"""

from sqlmodel import Session, create_engine, SQLModel, text
from core.config import settings
import logging

logger = logging.getLogger(__name__)

# Engine configurada para o Supabase (PostgreSQL)
engine = create_engine(
    settings.sqlalchemy_database_url,
    echo=not settings.is_production,
    pool_size=10,
    max_overflow=20
)

def init_db():
    """Cria as tabelas e realiza migrações automáticas de emergência."""
    try:
        # 1. Criar tabelas base
        SQLModel.metadata.create_all(engine)
        
        # 2. Migração de emergência: Adicionar logo_path se não existir
        # Usamos SQL puro para garantir compatibilidade com tabelas existentes
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE empresas ADD COLUMN IF NOT EXISTS logo_path TEXT;"))
            conn.commit()
            
        logger.info("Banco de dados sincronizado e migrado com sucesso.")
    except Exception as e:
        logger.error("Falha ao sincronizar/migrar banco de dados: %s", e)
        # Nao levantamos a exceção para permitir que o servidor FastAPI suba 
        # e possamos diagnosticar via health check ou logs de API.

def get_session():
    """Dependency para injeção de sessão nos endpoints do FastAPI."""
    with Session(engine) as session:
        yield session
