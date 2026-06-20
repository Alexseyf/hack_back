"""Pydantic models for Procedimento."""

from pydantic import BaseModel


class Procedimento(BaseModel):
    """Procedure reference data model."""

    id: str
    nome: str
    descricao: str
    duracao: str
    ordem: int
