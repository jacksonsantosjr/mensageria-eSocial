"""Schemas Pydantic de Empresa."""
from pydantic import BaseModel, Field
from typing import Optional

class EmpresaCreate(BaseModel):
    cnpj: str = Field(..., min_length=14, max_length=14)
    razao_social: str = Field(..., min_length=1, max_length=200)
    nome_fantasia: Optional[str] = Field(None, max_length=200)

class EmpresaUpdate(BaseModel):
    razao_social: Optional[str] = Field(None, max_length=200)
    nome_fantasia: Optional[str] = Field(None, max_length=200)
    ativo: Optional[bool] = None

class EmpresaResponse(BaseModel):
    id: str
    cnpj: str
    razao_social: str
    nome_fantasia: Optional[str] = None
    ativo: bool
    created_at: str
    updated_at: str
