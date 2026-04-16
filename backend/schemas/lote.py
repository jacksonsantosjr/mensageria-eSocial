"""Schemas Pydantic de Lote e Evento."""
import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional

class LoteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    empresa_id: uuid.UUID
    protocolo: Optional[str] = None
    status: str
    ambiente: str
    total_eventos: int = 0
    eventos_sucesso: int = 0
    eventos_erro: int = 0
    created_at: datetime
    updated_at: datetime

class EventoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    lote_id: uuid.UUID
    evento_id_esocial: Optional[str] = None
    tipo: Optional[str] = None
    status: str
    nr_recibo: Optional[str] = None
    cd_resposta: Optional[str] = None
    desc_resposta: Optional[str] = None
    ocorrencias_json: Optional[dict] = None
    validation_errors: Optional[dict] = None
    created_at: datetime
    updated_at: datetime

class LoteDetalheResponse(LoteResponse):
    eventos: list[EventoResponse] = []

class DashboardMetrics(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    total: int = 0
    pending: int = 0
    processed: int = 0
    errors: int = 0

class DashboardResumoResponse(BaseModel):
    metrics: DashboardMetrics
    recent_lotes: list[LoteResponse] = []
