"""
Gerenciamento de Sessão de Banco de Dados — eSocial Mensageria

Utiliza SQLModel para criar a engine e gerenciar o ciclo de vida
das sessões de banco de dados (Dependency Injection).
"""

from sqlmodel import Session, create_engine, SQLModel
from core.config import settings

# Engine configurada para o Supabase (PostgreSQL)
# echo=True pode ser ativado para debug de queries SQL em desenvolvimento
engine = create_engine(
    settings.sqlalchemy_database_url,
    echo=not settings.is_production,
    pool_size=10,
    max_overflow=20
)

import logging

logger = logging.getLogger(__name__)

def init_db():
    """Cria as tabelas no banco de dados (se nao existirem)."""
    try:
        SQLModel.metadata.create_all(engine)
        logger.info("Banco de dados sincronizado com sucesso.")
    except Exception as e:
        logger.error("Aviso: Falha ao sincronizar tabelas no startup: %s", e)
        # Nao levantamos a exceção para permitir que o servidor FastAPI suba 
        # e possamos diagnosticar via health check ou logs de API.

def get_session():
    """Dependency para injeção de sessão nos endpoints do FastAPI."""
    with Session(engine) as session:
        yield session
