"""Pydantic models for Paciente."""

from datetime import datetime
from pydantic import BaseModel, Field


class PacienteCreate(BaseModel):
    """Schema for creating a new patient."""

    nome: str = Field(..., min_length=1, examples=["João Silva"])
    idade: str = Field(..., min_length=1, examples=["7 anos"])
    responsavel: str = Field(default="", examples=["Maria Silva (mãe)"])
    condicao: str = Field(default="", examples=["Transtorno do Espectro Autista (TEA)"])
    comunicacao: str = Field(default="", examples=["Verbal com apoio"])
    sensibilidades: list[str] = Field(default_factory=list, examples=[["Toque", "Ruído"]])
    estrategia: str = Field(default="", examples=["Presença da mãe"])


class PacienteUpdate(BaseModel):
    """Schema for updating an existing patient (all fields optional)."""

    nome: str | None = None
    idade: str | None = None
    responsavel: str | None = None
    condicao: str | None = None
    comunicacao: str | None = None
    sensibilidades: list[str] | None = None
    estrategia: str | None = None


class Paciente(PacienteCreate):
    """Full patient model including database-generated fields."""

    id: str
    created_at: datetime
    updated_at: datetime
