"""Routes for Procedimentos (read-only reference data)."""

from fastapi import APIRouter, HTTPException
from neuro_api.database import get_supabase
from neuro_api.models.procedimento import Procedimento

router = APIRouter(prefix="/procedimentos", tags=["Procedimentos"])


@router.get("", response_model=list[Procedimento])
def listar_procedimentos():
    """List all procedures ordered by display order."""
    db = get_supabase()
    result = db.table("procedimentos").select("*").order("ordem").execute()
    return result.data


@router.get("/{procedimento_id}", response_model=Procedimento)
def buscar_procedimento(procedimento_id: str):
    """Get a single procedure by ID."""
    db = get_supabase()
    result = (
        db.table("procedimentos")
        .select("*")
        .eq("id", procedimento_id)
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=404, detail="Procedimento não encontrado")

    return result.data[0]
