import os
import time
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
    - Nível: Analista Pleno, Analista Sênior, Supervisão Sênior, Supervisora, Gerência, Diretoria ou HRBP (Business Partner).
    - Localidade: **Obrigatório/Foco Principal:** Presencial em Manaus, Amazonas (AM). Apenas considere opcionais vagas remotas se forem um encaixe absolutamente perfeito, mas priorize vagas locais em Manaus.
    - Skills principais: Formação em Gestão de RH, Sienge, Trello, gestão de equipes grandes (+300 funcionários), estruturação de processos.
    
    REGRAS DE ATUALIDADE (MUITO IMPORTANTE):
    - Atenção ao ano atual (estamos em abril de 2026).
    - Você DEVE descartar vagas que tenham datas de encerramento passadas, que sejam do ano de 2025 (ou mais velhas) ou onde o texto cite explicitamente que o processo seletivo foi "encerrado", "concluído" ou "pausado". Apenas considere vagas ativas.
    
    URL DA VAGA: {job_url}
    
    TEXTO DA VAGA:
    {job_text}
    
    TAREFA:
    Analise o texto fornecido da vaga. Verifique se é aderente ao perfil da candidata, focando no nível (Sênior/Gerência/Diretoria/HRBP) e localização (Manaus). É possível usar a URL também para checar a plataforma se necessário.
    
    RETORNO ESPERADO:
    Retorne **apenas** no formato abaixo. NÃO adicione nenhum texto introdutório ou conclusivo.
    Se a vaga for inativa (antiga/2025/encerrada), completamente irrelevante para Manaus (e não for remota) ou de perfil junior/assistente, retorne **vazio** ou diga 'DESCARTAR'.
    
    **[Título da Vaga] na [Nome da Empresa]**
    🔗 Link: {job_url}
    ⭐ Score: [Nota de 0 a 10 baseada na aderência ao perfil]
    📝 Justificativa: [Breve explicação de por que essa vaga se encaixa ou não no perfil]
    ---
    """
    
    for attempt in range(3):
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
            msg_erro = str(e)
            if "429" in msg_erro or "Quota" in msg_erro or "RESOURCE_EXHAUSTED" in msg_erro:
                print(f"    [Aviso] Limite do Gemini atingido. Aguardando 30s... (Tentativa {attempt+1}/3)")
                time.sleep(30)
            else:
                print(f"Erro ao consultar o Gemini para {job_url}: {e}")
                return None
                
    print(f"Falha ao consultar o Gemini após 3 tentativas para {job_url}")
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
