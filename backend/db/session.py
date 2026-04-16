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
    settings.database_url,
    echo=not settings.is_production,
    pool_size=10,
    max_overflow=20
)

def init_db():
    """Cria as tabelas no banco de dados (se nao existirem)."""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Dependency para injeção de sessão nos endpoints do FastAPI."""
    with Session(engine) as session:
        yield session
