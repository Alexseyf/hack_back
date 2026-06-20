"""Routes for Histórico de Atendimentos."""

from fastapi import APIRouter, HTTPException, Query
from neuro_api.database import get_supabase
from neuro_api.models.historico import HistoricoCreate, RegistroHistorico

router = APIRouter(prefix="/historico", tags=["Histórico"])


@router.get("", response_model=list[RegistroHistorico])
def listar_historico(limit: int = Query(default=20, ge=1, le=100)):
    """List attendance history, most recent first."""
    db = get_supabase()
    result = (
        db.table("historico_atendimentos")
        .select("*")
        .order("data_atendimento", desc=True)
        .limit(limit)
        .execute()
    )

    registros = []
    for row in result.data:
        # Fetch patient name for display
        pac = (
            db.table("pacientes")
            .select("nome, idade, condicao")
            .eq("id", row["paciente_id"])
            .execute()
        )
        # Fetch procedure name
        proc = (
            db.table("procedimentos")
            .select("nome")
            .eq("id", row["procedimento_id"])
            .execute()
        )

        paciente_data = pac.data[0] if pac.data else {}
        proc_data = proc.data[0] if proc.data else {}

        registro = RegistroHistorico(
            id=row["id"],
            paciente_id=row["paciente_id"],
            procedimento_id=row["procedimento_id"],
            orientacoes_json=row.get("orientacoes_json", []),
            data_atendimento=row["data_atendimento"],
            created_at=row["created_at"],
            paciente_nome=paciente_data.get("nome"),
            paciente_resumo=(
                f"{paciente_data.get('idade', '')} · {paciente_data.get('condicao', '')}"
                if paciente_data
                else None
            ),
            procedimento_nome=proc_data.get("nome"),
        )
        registros.append(registro)

    return registros


@router.post("", response_model=RegistroHistorico, status_code=201)
def salvar_historico(historico: HistoricoCreate):
    """Save an attendance record with orientations."""
    db = get_supabase()

    # Validate patient exists
    pac = (
        db.table("pacientes")
        .select("nome, idade, condicao")
        .eq("id", historico.paciente_id)
        .execute()
    )
    if not pac.data:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")

    # Validate procedure exists
    proc = (
        db.table("procedimentos")
        .select("nome")
        .eq("id", historico.procedimento_id)
        .execute()
    )
    if not proc.data:
        raise HTTPException(status_code=404, detail="Procedimento não encontrado")

    # Insert record
    insert_data = {
        "paciente_id": historico.paciente_id,
        "procedimento_id": historico.procedimento_id,
        "orientacoes_json": [o.model_dump() for o in historico.orientacoes_json],
    }
    result = db.table("historico_atendimentos").insert(insert_data).execute()

    if not result.data:
        raise HTTPException(status_code=500, detail="Erro ao salvar histórico")

    row = result.data[0]
    paciente_data = pac.data[0]
    proc_data = proc.data[0]

    return RegistroHistorico(
        id=row["id"],
        paciente_id=row["paciente_id"],
        procedimento_id=row["procedimento_id"],
        orientacoes_json=row.get("orientacoes_json", []),
        data_atendimento=row["data_atendimento"],
        created_at=row["created_at"],
        paciente_nome=paciente_data.get("nome"),
        paciente_resumo=f"{paciente_data.get('idade', '')} · {paciente_data.get('condicao', '')}",
        procedimento_nome=proc_data.get("nome"),
    )
