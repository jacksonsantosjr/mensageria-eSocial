"""Schemas Pydantic de Empresa."""
import uuid
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class EmpresaCreate(BaseModel):
    cnpj: str = Field(..., min_length=14, max_length=14)
    razao_social: str = Field(..., min_length=1, max_length=200)
    nome_fantasia: Optional[str] = Field(None, max_length=200)
    cert_base64: Optional[str] = None
    cert_password: Optional[str] = None

class EmpresaUpdate(BaseModel):
    razao_social: Optional[str] = Field(None, max_length=200)
    nome_fantasia: Optional[str] = Field(None, max_length=200)
    cert_base64: Optional[str] = None
    cert_password: Optional[str] = None
    ativo: Optional[bool] = None

class EmpresaResponse(BaseModel):
    id: uuid.UUID
    cnpj: str
    razao_social: str
    nome_fantasia: Optional[str] = None
    ativo: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
