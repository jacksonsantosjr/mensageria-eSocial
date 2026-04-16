"""
eSocial Mensageria — Aplicação Principal FastAPI

Sistema independente para transmissão de eventos do eSocial ao governo federal.
Responsável por validação XSD, assinatura digital (XMLDSIG) e consulta
assíncrona de protocolos via APScheduler.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from core.config import settings
from tasks.scheduler import start_scheduler, shutdown_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação: startup e shutdown."""
    start_scheduler()
    yield
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
    allow_origins=["*"],
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

# --- Frontend SPA Integration ---
FRONTEND_DIST = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")

if os.path.exists(FRONTEND_DIST):
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIST, "assets")), name="assets")

    # Catch-all para Rotas do React SPA (React Router)
    @app.get("/{full_path:path}")
    async def serve_react_app(full_path: str):
        index_path = os.path.join(FRONTEND_DIST, "index.html")
        return FileResponse(index_path)
