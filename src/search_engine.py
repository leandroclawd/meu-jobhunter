import os
import time
import requests
from bs4 import BeautifulSoup

from ddgs import DDGS

def duckduckgo_search_jobs(query, num_results=5):
    """Realiza a busca usando DuckDuckGo Search (sem necessidade de chaves)."""
    urls = []
    print(f"Buscando com DuckDuckGo: {query}")
    try:
        with DDGS() as ddgs:
            # max_results controla quantas paginas ele traz
            # timelimit='m' garante resultados apenas do ultimo mes (vagas recentes/ativas)
            results = ddgs.text(query, max_results=num_results, timelimit='m')
            for res in results:
                if 'href' in res:
                    urls.append(res['href'])
    except Exception as e:
        print(f"Erro na API do DuckDuckGo: {e}")
        
    return urls

def extract_job_text(url):
    """Acessa a URL da vaga e extrai o texto principal."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove scripts e styles
        for script in soup(["script", "style", "noscript"]):
            script.extract()
            
        text = soup.get_text(separator=' ', strip=True)
        return text
    except Exception as e:
        print(f"Erro ao extrair texto da URL {url}: {e}")
        return ""

def get_job_opportunities():
    """Busca vagas usando os dorks configurados."""
    
    queries = [
        # Dorks originais refinados (Adicionado subdiretórios de vagas para evitar páginas de avaliações/lixo)
        'site:gupy.io/job "Recursos Humanos" "Manaus" -remoto',
        'site:br.indeed.com/viewjob "Recursos Humanos" "Manaus"',
        'site:infojobs.com.br/emprego "Recursos Humanos" "Manaus"',
        'site:catho.com.br/vagas "Recursos Humanos" "Manaus"',
        'site:amazonempregos.com.br "RH" "Manaus"',
        'site:boards.greenhouse.io "Recursos Humanos" "Manaus"',
        'site:jobs.lever.co "Recursos Humanos" "Manaus"',
        
        # Dorks Adicionadas e filtradas
        'site:gupy.io/job "RH" "Manaus"',
        'site:vagas.com.br/vagas "Recursos Humanos" "Manaus"',
        'site:vagas.com.br/vagas "RH" "Manaus"',
        'site:br.indeed.com/viewjob "RH" "Manaus"',
        'site:catho.com.br/vagas "RH" "Manaus"',
        'site:solides.jobs/vaga "Recursos Humanos" "Manaus"',
        'site:solides.jobs/vaga "RH" "Manaus"',
        'site:trabalhabrasil.com.br/vagas-empregos "Recursos Humanos" "Manaus"',
        'site:trabalhabrasil.com.br/vagas-empregos "RH" "Manaus"',
    ]
    
    jobs_data = []
    for dork in queries:
        print(f"[*] Buscando com a dork: {dork}")
        urls = duckduckgo_search_jobs(dork, num_results=10)
        
        for url in urls:
            print(f"[*] Extraindo dados de: {url}")
            text = extract_job_text(url)
            if text:
                jobs_data.append({
                    "url": url,
                    "text": text[:4000]
                })
        time.sleep(4) # Pausa estratégica para evitar bloqueios do DuckDuckGo
                
    return jobs_data

if __name__ == "__main__":
    # Teste requer as variaveis de ambiente setadas
    from dotenv import load_dotenv
    load_dotenv()
    
    jobs = get_job_opportunities()
    print(f"\nTotal de vagas: {len(jobs)}")
