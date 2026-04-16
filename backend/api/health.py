from fastapi import APIRouter, Depends
from sqlmodel import Session, text
from core.config import settings
from db.session import get_session

router = APIRouter()

@router.get("/health")
async def health_check():
    """Retorna status da aplicacao, versao e ambiente."""
    return {
        "status": "ok",
        "version": "1.0.0",
        "environment": settings.environment,
        "mock_mode": settings.mock_esocial,
    }

@router.get("/health/db")
async def db_health_check(session: Session = Depends(get_session)):
    """Verifica se as colunas essenciais existem no banco."""
    tables = ["empresas", "lotes", "eventos"]
    results = {}
    try:
        for table in tables:
            query = text(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table}';")
            cols = session.execute(query).all()
            results[table] = [c[0] for c in cols]
        return {"status": "connected", "schema": results}
    except Exception as e:
        return {"status": "error", "message": str(e)}
