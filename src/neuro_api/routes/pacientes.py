"""CRUD routes for Pacientes."""

from fastapi import APIRouter, HTTPException, Query
from neuro_api.database import get_supabase
from neuro_api.models.paciente import Paciente, PacienteCreate, PacienteUpdate

router = APIRouter(prefix="/pacientes", tags=["Pacientes"])


@router.get("", response_model=list[Paciente])
def listar_pacientes(q: str | None = Query(None, description="Buscar por nome ou condição")):
    """List all patients, optionally filtering by name or condition."""
    db = get_supabase()
    query = db.table("pacientes").select("*").order("nome")

    if q:
        # Search by name or condition (case-insensitive)
        query = query.or_(f"nome.ilike.%{q}%,condicao.ilike.%{q}%")

    result = query.execute()
    return result.data


@router.get("/{paciente_id}", response_model=Paciente)
def buscar_paciente(paciente_id: str):
    """Get a single patient by ID."""
    db = get_supabase()
    result = db.table("pacientes").select("*").eq("id", paciente_id).execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")

    return result.data[0]


@router.post("", response_model=Paciente, status_code=201)
def criar_paciente(paciente: PacienteCreate):
    """Create a new patient."""
    db = get_supabase()
    result = db.table("pacientes").insert(paciente.model_dump()).execute()

    if not result.data:
        raise HTTPException(status_code=500, detail="Erro ao criar paciente")

    return result.data[0]


@router.put("/{paciente_id}", response_model=Paciente)
def atualizar_paciente(paciente_id: str, paciente: PacienteUpdate):
    """Update an existing patient."""
    db = get_supabase()

    # Only update fields that were explicitly set
    update_data = paciente.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="Nenhum campo para atualizar")

    result = (
        db.table("pacientes")
        .update(update_data)
        .eq("id", paciente_id)
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")

    return result.data[0]


@router.delete("/{paciente_id}", status_code=204)
def remover_paciente(paciente_id: str):
    """Delete a patient by ID."""
    db = get_supabase()
    result = db.table("pacientes").delete().eq("id", paciente_id).execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")

    return None
