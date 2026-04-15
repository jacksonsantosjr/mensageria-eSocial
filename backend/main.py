"""
eSocial Mensageria — Aplicação Principal FastAPI

Sistema independente para transmissão de eventos do eSocial ao governo federal.
Responsável por validação XSD, assinatura digital (XMLDSIG) e consulta
assíncrona de protocolos via APScheduler.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from tasks.scheduler import start_scheduler, shutdown_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação: startup e shutdown."""
    # --- Startup ---
    start_scheduler()
    yield
    # --- Shutdown ---
    shutdown_scheduler()


app = FastAPI(
    title="eSocial Mensageria",
    description="Sistema de transmissão de eventos do eSocial com validação XSD, assinatura digital e consulta assíncrona.",
    version="1.0.0",
    lifespan=lifespan,
)

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routers ---
from api.health import router as health_router
from api.empresas import router as empresas_router
from api.lotes import router as lotes_router

app.include_router(health_router, prefix="/api", tags=["Health"])
app.include_router(empresas_router, prefix="/api", tags=["Empresas"])
app.include_router(lotes_router, prefix="/api", tags=["Lotes"])
