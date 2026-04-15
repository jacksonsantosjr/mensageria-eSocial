"""
Rota de Health Check
"""
from fastapi import APIRouter
from core.config import settings

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
