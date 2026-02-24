import os
from google import genai
from google.genai import types

def evaluate_job(job_url, job_text):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Erro: GEMINI_API_KEY não encontrada no .env")
        return None
        
    client = genai.Client(api_key=api_key)
    
    prompt = f"""
    Você é um assistente de recrutamento executivo. O seu objetivo é analisar uma vaga de emprego na área de Recursos Humanos.
    
    PERFIL DA CANDIDATA:
    - Nível: Analista Sênior, Supervisão Sênior, Supervisora, Gerência, Diretoria ou HRBP (Business Partner).
    - Localidade: **Obrigatório/Foco Principal:** Presencial em Manaus, Amazonas (AM). Apenas considere opcionais vagas remotas se forem um encaixe absolutamente perfeito, mas priorize vagas locais em Manaus.
    - Skills principais: Formação em Gestão de RH, Sienge, Trello, gestão de equipes grandes (+300 funcionários), estruturação de processos.
    
    URL DA VAGA: {job_url}
    
    TEXTO DA VAGA:
    {job_text}
    
    TAREFA:
    Analise o texto fornecido da vaga. Verifique se é aderente ao perfil da candidata, focando no nível (Sênior/Gerência/Diretoria/HRBP) e localização (Manaus). É possível usar a URL também para checar a plataforma se necessário.
    
    RETORNO ESPERADO:
    Retorne **apenas** no formato abaixo. NÃO adicione nenhum texto introdutório ou conclusivo.
    Se a vaga for completamente irrelevante para Manaus (e não for expressamente remota) ou for de nível júnior/assistente, retorne **vazio** ou diga 'DESCARTAR'.
    
    **[Título da Vaga] na [Nome da Empresa]**
    🔗 Link: {job_url}
    ⭐ Score: [Nota de 0 a 10 baseada na aderência ao perfil]
    📝 Justificativa: [Breve explicação de por que essa vaga se encaixa ou não no perfil]
    ---
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt,
        )
        # Se a IA decidiu descartar essa vaga, não retornamos nada
        if "DESCARTAR" in response.text.upper():
            return None
        return response.text
    except Exception as e:
        print(f"Erro ao consultar o Gemini para {job_url}: {e}")
        return None

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    # Exemplo mock para teste da nova assinatura do ai_agent
    url_teste = "https://gupy.io/vaga-teste"
    texto_teste = "A empresa XPTO está buscando um Gerente de RH Sênior em Manaus com foco em estratégias."
    print("Testando avaliador do Gemini...")
    resultado = evaluate_job(url_teste, texto_teste)
    print(resultado)
