"""
Script de Migração Manual — eSocial Mensageria
Adiciona a coluna logo_path à tabela empresas caso ela não exista.
"""
from sqlmodel import create_engine, text
from core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate():
    engine = create_engine(settings.sqlalchemy_database_url)
    
    with engine.connect() as conn:
        logger.info("Verificando estrutura da tabela 'empresas'...")
        try:
            # Comando SQL para adicionar a coluna de forma segura (PostgreSQL / Supabase)
            # O bloco anônimo garante que não falhe se a coluna já existir por algum motivo
            conn.execute(text("""
                DO $$
                BEGIN
                    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                   WHERE table_name='empresas' AND column_name='logo_path') THEN
                        ALTER TABLE empresas ADD COLUMN logo_path TEXT;
                        RAISE NOTICE 'Coluna logo_path adicionada com sucesso.';
                    END IF;
                END $$;
            """))
            conn.commit()
            logger.info("Migração concluída com sucesso.")
        except Exception as e:
            logger.error("Falha ao executar migração: %s", e)
            raise

if __name__ == "__main__":
    migrate()
