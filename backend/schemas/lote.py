"""Schemas Pydantic de Lote e Evento."""
from pydantic import BaseModel
from typing import Optional

class LoteResponse(BaseModel):
    id: str
    empresa_id: str
    protocolo: Optional[str] = None
    status: str
    ambiente: str
    total_eventos: int
    eventos_sucesso: int
    eventos_erro: int
    created_at: str
    updated_at: str

class EventoResponse(BaseModel):
    id: str
    lote_id: str
    evento_id_esocial: Optional[str] = None
    tipo: Optional[str] = None
    status: str
    nr_recibo: Optional[str] = None
    cd_resposta: Optional[str] = None
    desc_resposta: Optional[str] = None
    ocorrencias_json: Optional[dict] = None
    validation_errors: Optional[dict] = None
    created_at: str
    updated_at: str

class LoteDetalheResponse(LoteResponse):
    eventos: list[EventoResponse] = []

class DashboardResumo(BaseModel):
    total: int
    pendentes: int
    enviados: int
    processados: int
    com_erro: int
