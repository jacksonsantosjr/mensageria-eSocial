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
        
        # 2. Migração de emergência: Sincronização de Schemas
        with engine.connect() as conn:
            # Tabela Empresas
            conn.execute(text("ALTER TABLE empresas ADD COLUMN IF NOT EXISTS logo_path TEXT;"))
            
            # Tabela Lotes
            conn.execute(text("ALTER TABLE lotes ADD COLUMN IF NOT EXISTS xml_original TEXT;"))
            conn.execute(text("ALTER TABLE lotes ADD COLUMN IF NOT EXISTS xml_assinado TEXT;"))
            conn.execute(text("ALTER TABLE lotes ADD COLUMN IF NOT EXISTS total_eventos INTEGER DEFAULT 0;"))
            conn.execute(text("ALTER TABLE lotes ADD COLUMN IF NOT EXISTS eventos_sucesso INTEGER DEFAULT 0;"))
            conn.execute(text("ALTER TABLE lotes ADD COLUMN IF NOT EXISTS eventos_erro INTEGER DEFAULT 0;"))
            conn.execute(text("ALTER TABLE lotes ADD COLUMN IF NOT EXISTS erro_geral TEXT;"))
            conn.execute(text("ALTER TABLE lotes ADD COLUMN IF NOT EXISTS tentativas_consulta INTEGER DEFAULT 0;"))
            conn.execute(text("ALTER TABLE lotes ADD COLUMN IF NOT EXISTS proxima_consulta TIMESTAMP;"))
            
            # Tabela Eventos
            conn.execute(text("ALTER TABLE eventos ADD COLUMN IF NOT EXISTS evento_id_esocial TEXT;"))
            conn.execute(text("ALTER TABLE eventos ADD COLUMN IF NOT EXISTS tipo TEXT;"))
            conn.execute(text("ALTER TABLE eventos ADD COLUMN IF NOT EXISTS xml_original TEXT;"))
            conn.execute(text("ALTER TABLE eventos ADD COLUMN IF NOT EXISTS xml_assinado TEXT;"))
            conn.execute(text("ALTER TABLE eventos ADD COLUMN IF NOT EXISTS status TEXT;"))
            conn.execute(text("ALTER TABLE eventos ADD COLUMN IF NOT EXISTS nr_recibo TEXT;"))
            conn.execute(text("ALTER TABLE eventos ADD COLUMN IF NOT EXISTS cd_resposta TEXT;"))
            conn.execute(text("ALTER TABLE eventos ADD COLUMN IF NOT EXISTS desc_resposta TEXT;"))
            conn.execute(text("ALTER TABLE eventos ADD COLUMN IF NOT EXISTS ocorrencias_json JSONB;"))
            conn.execute(text("ALTER TABLE eventos ADD COLUMN IF NOT EXISTS validation_errors JSONB;"))
            
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
