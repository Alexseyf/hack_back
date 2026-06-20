"""Routes for generating personalized care orientations."""

from fastapi import APIRouter, HTTPException
from neuro_api.database import get_supabase
from neuro_api.models.historico import GerarOrientacoesRequest, Orientacao
from neuro_api.services.ai_agent import gerar_orientacoes_ia

router = APIRouter(prefix="/orientacoes", tags=["Orientações"])


def gerar_orientacoes_fallback(paciente: dict, procedimento_nome: str) -> list[Orientacao]:
    """Generate personalized care orientations using static fallback logic.

    Used when the AI agent is unavailable.
    """
    sens: list[str] = paciente.get("sensibilidades", [])
    lista_sens = ", ".join(sens).lower() if sens else "sensibilidades não informadas"
    proc = procedimento_nome.lower()
    comunicacao = paciente.get("comunicacao", "não informada").lower()
    estrategia = paciente.get("estrategia", "acolhimento individualizado").lower()
    responsavel = paciente.get("responsavel", "o acompanhante")

    evitar_extra = (
        "Priorize o atendimento e reduza o tempo em ambientes cheios."
        if "Espera longa" in sens or "Excesso de estímulos" in sens
        else "Não force o contato físico nem mude a rotina sem avisar."
    )

    return [
        Orientacao(
            categoria="Antes do atendimento",
            descricao=(
                f'Apresente-se com calma e explique o que será feito em {proc}. '
                f'Mostre os materiais antes de usar e confirme o entendimento, '
                f'já que a comunicação é "{comunicacao}". '
                f'Garanta a estratégia que funciona: {estrategia}.'
            ),
        ),
        Orientacao(
            categoria="Durante o procedimento",
            descricao=(
                f"Avise antes de cada toque ou som. Faça pausas curtas se houver "
                f"sinais de desconforto e use frases objetivas. Mantenha "
                f"{responsavel} por perto para transmitir segurança."
            ),
        ),
        Orientacao(
            categoria="O que evitar",
            descricao=(
                f"Evite estímulos ligados às sensibilidades do paciente: "
                f"{lista_sens}. {evitar_extra}"
            ),
        ),
        Orientacao(
            categoria="Se houver resistência ou desregulação",
            descricao=(
                "Interrompa o procedimento, leve a um espaço tranquilo e reduza "
                "luz e ruído. Dê tempo para regulação, valide o sentimento e "
                "retome apenas quando houver sinais de calma."
            ),
        ),
        Orientacao(
            categoria="Registrar para a próxima vez",
            descricao=(
                "Anote o que funcionou e o que gerou desconforto no prontuário. "
                "Esse registro ajuda toda a equipe a oferecer um atendimento "
                "mais previsível no próximo encontro."
            ),
        ),
    ]


@router.post("/gerar", response_model=list[Orientacao])
def gerar(request: GerarOrientacoesRequest):
    """Generate personalized care orientations for a patient and procedure."""
    db = get_supabase()

    # Check if there is already a record for this patient and procedure
    historico_result = (
        db.table("historico_atendimentos")
        .select("orientacoes_json")
        .eq("paciente_id", request.paciente_id)
        .eq("procedimento_id", request.procedimento_id)
        .order("data_atendimento", desc=True)
        .limit(1)
        .execute()
    )

    # Se já existir no banco, usamos o registro mais recente em vez de gastar cota da IA
    if historico_result.data and historico_result.data[0].get("orientacoes_json"):
        print("Histórico encontrado! Retornando orientações do banco de dados.")
        return historico_result.data[0]["orientacoes_json"]

    pac_result = (
        db.table("pacientes")
        .select("*")
        .eq("id", request.paciente_id)
        .execute()
    )
    if not pac_result.data:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")

    proc_result = (
        db.table("procedimentos")
        .select("*")
        .eq("id", request.procedimento_id)
        .execute()
    )
    if not proc_result.data:
        raise HTTPException(status_code=404, detail="Procedimento não encontrado")

    paciente = pac_result.data[0]
    procedimento = proc_result.data[0]

    try:
        orientacoes = gerar_orientacoes_ia(paciente, procedimento)
        print("Nenhum histórico encontrado. Gerado novo via IA.")
    except Exception as e:
        print(f"Erro na IA (fallback ativado): {e}")
        orientacoes = gerar_orientacoes_fallback(paciente, procedimento["nome"])
        
    return orientacoes
