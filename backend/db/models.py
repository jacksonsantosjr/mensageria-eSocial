"""
Modelos de Banco de Dados — eSocial Mensageria

Define os modelos SQLModel para as tabelas: Empresa, Lote e Evento.
Suporte multi-tenant via tabela Empresa (múltiplos CNPJs).
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel, Relationship, Column
from sqlalchemy import JSON


# --- Enums ---

class LoteStatus(str, Enum):
    """Status possíveis de um lote."""
    PENDING = "PENDING"
    VALIDATING = "VALIDATING"
    SIGNED = "SIGNED"
    SENT = "SENT"
    PROCESSING = "PROCESSING"
    PROCESSED = "PROCESSED"
    ERROR = "ERROR"


class EventoStatus(str, Enum):
    """Status possíveis de um evento individual."""
    PENDING = "PENDING"
    VALID = "VALID"
    INVALID = "INVALID"
    SIGNED = "SIGNED"
    SENT = "SENT"
    PROCESSED = "PROCESSED"
    ERROR = "ERROR"


class Ambiente(str, Enum):
    """Ambientes do eSocial."""
    PRODUCTION = "PRODUCTION"
    HOMOLOGATION = "HOMOLOGATION"


# --- Modelos ---

class Empresa(SQLModel, table=True):
    """Empresa (multi-tenant) — cada CNPJ empregador do grupo empresarial."""
    __tablename__ = "empresas"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    cnpj: str = Field(max_length=14, unique=True, index=True)
    razao_social: str = Field(max_length=200)
    nome_fantasia: Optional[str] = Field(default=None, max_length=200)
    cert_base64: Optional[str] = Field(default=None)
    cert_password: Optional[str] = Field(default=None, max_length=200)
    ativo: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @property
    def certificado_a1(self) -> bool:
        """Indica se a empresa possui certificado configurado."""
        return bool(self.cert_base64)

    # Relacionamentos
    lotes: list["Lote"] = Relationship(back_populates="empresa")


class Lote(SQLModel, table=True):
    """Lote de eventos do eSocial — agrupamento de eventos para envio."""
    __tablename__ = "lotes"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    empresa_id: uuid.UUID = Field(foreign_key="empresas.id", index=True)
    protocolo: Optional[str] = Field(default=None, max_length=50)
    status: LoteStatus = Field(default=LoteStatus.PENDING)
    ambiente: Ambiente = Field(default=Ambiente.HOMOLOGATION)
    grupo_evento: Optional[int] = Field(default=None)
    xml_original: Optional[str] = Field(default=None)
    xml_assinado: Optional[str] = Field(default=None)
    total_eventos: int = Field(default=0)
    eventos_sucesso: int = Field(default=0)
    eventos_erro: int = Field(default=0)
    erro_geral: Optional[str] = Field(default=None)
    tentativas_consulta: int = Field(default=0)
    proxima_consulta: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relacionamentos
    empresa: Optional[Empresa] = Relationship(back_populates="lotes")
    eventos: list["Evento"] = Relationship(back_populates="lote")


class Evento(SQLModel, table=True):
    """Evento individual do eSocial dentro de um lote."""
    __tablename__ = "eventos"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    lote_id: uuid.UUID = Field(foreign_key="lotes.id", index=True)
    evento_id_esocial: Optional[str] = Field(default=None, max_length=100)
    tipo: Optional[str] = Field(default=None, max_length=20)
    xml_original: Optional[str] = Field(default=None)
    xml_assinado: Optional[str] = Field(default=None)
    status: EventoStatus = Field(default=EventoStatus.PENDING)
    nr_recibo: Optional[str] = Field(default=None, max_length=50)
    cd_resposta: Optional[str] = Field(default=None, max_length=10)
    desc_resposta: Optional[str] = Field(default=None)
    ocorrencias_json: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    validation_errors: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relacionamentos
    lote: Optional[Lote] = Relationship(back_populates="eventos")


class SystemConfig(SQLModel, table=True):
    """Configurações globais do sistema."""
    __tablename__ = "system_config"

    key: str = Field(primary_key=True)
    value: str = Field(max_length=50)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
