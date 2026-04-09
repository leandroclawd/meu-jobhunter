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
    Você é um assistente de recrutamento executivo implacável. O seu objetivo é analisar uma vaga de emprego na área de Recursos Humanos e descartar severamente tudo que saia da regra do usuário.
    
    PERFIL DA CANDIDATA:
    - Nível: Analista Pleno, Analista Sênior, Supervisão Sênior, Supervisora, Gerência, Diretoria ou HRBP (Business Partner).
    - Localidade: **EXTREMAMENTE OBRIGATÓRIO:** Vaga PRESENCIAL (ou modelo Híbrido se a base for) na cidade de **Manaus, Amazonas (AM)**.
    - Skills principais: Formação em Gestão de RH, Sienge, Trello, gestão de equipes grandes (+300 funcionários), estruturação de processos.
    
    REGRAS DE DESCARTE (MUITO IMPORTANTE):
    Você DEVE retornar a palavra DESCARTAR se qualquer uma dessas coisas acontecer:
    1. A vaga for de qualquer outra cidade/estado que NÃO seja Manaus-AM.
    2. A vaga for no modelo "100% Remoto" ou "Home Office". O usuário DEIXOU CLARO que quer vagas presenciais em Manaus.
    3. A vaga for de nível muito iniciante (Júnior, Assistente ou Estágio).
    4. A vaga citar explicitlyamente que o processo foi encerrado, é do ano de 2025 ou mais velha.
    
    URL DA VAGA: {job_url}
    
    TEXTO DA VAGA:
    {job_text}
    
    TAREFA:
    Analise o texto fornecido da vaga. Se ela desrespeitar qualquer uma das REGRAS DE DESCARTE acima, retorne "DESCARTAR". Se for uma vaga ativa, Sênior/Gerência de RH e **fisicamente baseada em Manaus/AM**, passe-a adiante.
    
    RETORNO ESPERADO:
    Retorne **apenas** no formato abaixo. NÃO adicione nenhum texto introdutório ou conclusivo.
    Se falhar na regra, retorne **apenas** a palavra 'DESCARTAR'.
    
    **[Título da Vaga] na [Nome da Empresa]**
    🔗 Link: {job_url}
    ⭐ Score: [Nota de 0 a 10 baseada na aderência ao perfil]
    📝 Justificativa: [Breve explicação de por que essa vaga se encaixa]
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
