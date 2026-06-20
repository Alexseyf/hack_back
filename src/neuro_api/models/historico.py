"""Pydantic models for Histórico de Atendimentos."""

from datetime import datetime
from pydantic import BaseModel, Field


class Orientacao(BaseModel):
    """A single care orientation item."""

    categoria: str
    descricao: str


class HistoricoCreate(BaseModel):
    """Schema for saving an attendance record."""

    paciente_id: str = Field(..., examples=["550e8400-e29b-41d4-a716-446655440000"])
    procedimento_id: str = Field(..., examples=["medicacao"])
    orientacoes_json: list[Orientacao] = Field(default_factory=list)


class RegistroHistorico(BaseModel):
    """Full attendance history record."""

    id: str
    paciente_id: str
    procedimento_id: str
    orientacoes_json: list[Orientacao] | list[dict] = Field(default_factory=list)
    data_atendimento: datetime
    created_at: datetime
    # Joined fields (from query)
    paciente_nome: str | None = None
    paciente_resumo: str | None = None
    procedimento_nome: str | None = None


class GerarOrientacoesRequest(BaseModel):
    """Request body to generate personalized care orientations."""

    paciente_id: str
    procedimento_id: str
