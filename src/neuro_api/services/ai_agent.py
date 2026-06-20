import json
from google import genai
from neuro_api.config import settings
from neuro_api.models.historico import Orientacao
from pydantic import BaseModel

class OrientacaoList(BaseModel):
    orientacoes: list[Orientacao]

def gerar_orientacoes_ia(paciente: dict, procedimento: dict) -> list[Orientacao]:
    """
    Usa o modelo LLM do Google Gemini para gerar orientações personalizadas 
    com base no perfil do paciente e no procedimento clínico.
    """
    if not settings.GEMINI_API_KEY:
        raise ValueError("Chave da API do Gemini (GEMINI_API_KEY) não configurada.")
    
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    
    system_instruction = """Você é um especialista em neuropsicologia, TEA e acessibilidade na área da saúde.
Sua função é fornecer orientações de atendimento clínico precisas e individualizadas para profissionais de saúde lidarem com pacientes neurodivergentes.
Você DEVE agrupar as orientações em EXATAMENTE 5 categorias estritas, criando um texto altamente conciso.
As categorias OBRIGATÓRIAS e únicas permitidas são:
1. "Antes do atendimento"
2. "Durante o procedimento"
3. "O que evitar"
4. "Se houver resistência ou desregulação"
5. "Registrar para a próxima vez"

Regra de formatação: Seja extremamente objetivo, direto e prático. Use, no máximo, 2 frases curtas por categoria. Evite explicações teóricas.
Não crie outras categorias além dessas. Retorne APENAS um JSON estruturado com uma lista contendo exatamente 5 objetos, um para cada categoria."""
    
    prompt = f"""
Perfil do Paciente:
- Nome: {paciente.get('nome')}
- Condição: {paciente.get('condicao')}
- Idade: {paciente.get('idade')} anos
- Comunicação: {paciente.get('comunicacao')}
- Sensibilidades: {paciente.get('sensibilidades', 'Não informadas')}
- Estratégia recomendada: {paciente.get('estrategia_recomendada')}

Procedimento Médico a ser realizado:
- Nome: {procedimento.get('nome')}
- Descrição: {procedimento.get('descricao', 'Sem descrição específica')}

Gere as orientações curtas e diretas seguindo estritamente as 5 categorias obrigatórias acima. Limite o texto a 2 frases por categoria, focado exclusivamente na ação prática que o profissional de saúde deve tomar.
"""
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=genai.types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
            response_schema=OrientacaoList,
            temperature=0.4, # Temperatura mais baixa para respostas mais assertivas/clínicas
        ),
    )
    
    # Faz o parse da resposta JSON retornada pelo Gemini e converte para objetos Pydantic
    try:
        result_dict = json.loads(response.text)
        return [Orientacao(**item) for item in result_dict.get("orientacoes", [])]
    except Exception as e:
        raise RuntimeError(f"Falha ao processar o JSON da IA: {str(e)}")
