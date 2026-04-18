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
    
    base_queries = [
        # Dorks originais refinados
        'site:gupy.io/job "Recursos Humanos" "Manaus" -remoto',
        'site:br.indeed.com/viewjob "Recursos Humanos" "Manaus"',
        'site:infojobs.com.br/emprego "Recursos Humanos" "Manaus"',
        'site:catho.com.br/vagas "Recursos Humanos" "Manaus"',
        'site:amazonempregos.com.br "RH" "Manaus"',
        'site:boards.greenhouse.io "Recursos Humanos" "Manaus"',
        'site:jobs.lever.co "Recursos Humanos" "Manaus"',
        
        # LinkedIn (Adicionado conforme solicitado)
        'site:linkedin.com/jobs/view "Recursos Humanos" "Manaus"',
        'site:linkedin.com/jobs/search "Recursos Humanos" "Manaus"',
        
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
    
    # Exclusões para evitar vagas de outros estados e falsos positivos
    exclusions = '-Camaçari -Campinas -Bahia -SP -RJ -MG -PR -SC -RS -PE -Pernambuco -Recife -CE -Fortaleza -site:ingles.com -site:inglês.com -site:cambridge.org -site:spanishdict.com -site:glosbe.com -dictionary -dicionario -headlight -farol -carro -peças -automotivo -automotive -site:.cl "naturales" "recursos naturais" -renda -ganhar -dinheiro -online -extra -afiliado -turismo -viagem -hotel -pousada -restaurante'
    
    queries = [f"{q} {exclusions}" for q in base_queries]
    
    jobs_data = []
    
    # Lista de domínios proibidos (filtro extra no Python)
    banned_domains = [
        'ingles.com', 'dicionario', 'dictionary', 'translation', 'cambridge.org', 
        'significado', 'tradutor', 'spanishdict.com', 'glosbe.com',
        'chevyavalanchefanclub.com', 'forum', 'clubedo', 'mecanica', 'autopecas',
        'wikipedia.org', 'pt.wikipedia.org', 'en.wikipedia.org', '.pdf', 'millaray-temuco.cl',
        'tiktok.com', 'facebook.com', 'instagram.com', 'twitter.com', 'x.com',
        'mobills.com.br', 'meupaitrabalha', 'vagas.com.br/blog', 'gupy.io/blog', 'gupy.io/blog-do-emprego',
        'blog.gupy.io', 'vagas.com.br/educacao', 'melhoresdestinos.com.br', 'tripadvisor', 'trivago',
        'bahiaeconomica.com.br', 'alagoinhas', 'feiradesantana', 'mundoconectado.com.br', 'canaltech', 'tecmundo'
    ]

    for dork in queries:
        print(f"[*] Buscando com a dork: {dork}")
        urls = duckduckgo_search_jobs(dork, num_results=10)
        
        for url in urls:
            # Pula se for um site banido ou arquivo PDF
            if any(b in url.lower() for b in banned_domains) or url.lower().endswith('.pdf'):
                continue
                
            print(f"[*] Extraindo dados de: {url}")
            text = extract_job_text(url)
            # Filtro extra no texto para garantir que "RH" é Recursos Humanos e não "Right Hand" ou "Recursos Naturais"
            if text:
                lower_text = text.lower()
                
                # Validação de Cidade (Manaus deve ser a estrela, não Camaçari/Bahia)
                forbidden_cities = ['camaçari', 'alagoinhas', 'salvador', 'recife', 'fortaleza', 'rio de janeiro', 'são paulo', 'curitiba']
                if any(city in lower_text for city in forbidden_cities):
                    # Se tiver Manaus E uma cidade proibida, verificamos se Manaus parece ser apenas menção secundária
                    if 'manaus' not in lower_text:
                        continue
                    # Se Camaçari aparecer mais que Manaus, provavelmente é de lá
                    if lower_text.count('camaçari') > lower_text.count('manaus'):
                        continue

                # Descartar se falar de recursos naturais ou guias escolares
                if any(term in lower_text for term in ['naturales', 'recursos naturais', 'guia de estudo', 'clase', 'educación']):
                    if not any(term in lower_text for term in ['vaga', 'contrata', 'currículo', 'analista']):
                        continue

                # Validação especial para sites governamentais (apenas se for vaga/concurso/seleção)
                if 'gov.br' in url.lower():
                    if not any(term in lower_text for term in ['vaga', 'concurso', 'processo seletivo', 'contratação', 'emprego', 'rh', 'recursos humanos']):
                        continue

                jobs_data.append({
                    "url": url,
                    "text": text[:4000]
                })
        time.sleep(4) # Pausa estratégica para evitar bloqueios do DuckDuckGo
                
    return jobs_data

def get_business_leads():
    """Busca notícias sobre expansões e novas empresas em Manaus."""
    # Adicionamos as mesmas exclusões para os leads
    exclusions = '-headlight -farol -carro -peças -automotivo -automotive -forum -site:.cl "naturales" "recursos naturais" -renda -ganhar -dinheiro -online -turismo -viagem -PE -Recife -CE -Fortaleza'
    
    queries = [
        f'"inauguração" Manaus empresa {exclusions}',
        f'"nova fábrica" Manaus {exclusions}',
        f'"ampliação" Manaus fábrica {exclusions}',
        f'"investimento" Manaus indústria notícia {exclusions}',
        f'"contratação" Manaus "Recursos Humanos" empresa novas {exclusions}' # Trocamos RH por "Recursos Humanos" aqui para ser mais preciso
    ]
    
    leads = []
    seen_urls = set()
    banned_domains = ['forum', 'clubedo', 'mecanica', 'chevyavalanchefanclub.com', 'wikipedia.org', 'millaray-temuco.cl', 'tiktok.com', 'facebook.com', 'instagram.com', 'mobills.com.br', 'gupy.io/blog', 'vagas.com.br/blog', 'melhoresdestinos.com.br', 'tripadvisor', 'bahiaeconomica.com.br', 'mundoconectado.com.br']
    
    for q in queries:
        print(f"[*] Buscando leads de negócios: {q}")
        urls = duckduckgo_search_jobs(q, num_results=5)
        for url in urls:
            if url not in seen_urls:
                if any(b in url.lower() for b in banned_domains):
                    continue

                # Extraímos apenas o título/texto básico para o card
                text = extract_job_text(url)
                if text:
                    lower_text = text.lower()
                    # Filtro para sites governamentais (apenas se for relevante para emprego/negócios)
                    if 'gov.br' in url.lower():
                        if not any(term in lower_text for term in ['vaga', 'concurso', 'contratação', 'emprego', 'rh', 'recursos humanos', 'investimento', 'fábrica', 'empresa']):
                            continue

                    # Filtro de conteúdo mínimo
                    if len(text) < 500: continue
                    
                    leads.append({
                        "url": url,
                        "title": text[:100].strip() + "...",
                        "snippet": text[:300].strip() + "..."
                    })
                    seen_urls.add(url)
        time.sleep(2)
        
    return leads

if __name__ == "__main__":
    # Teste requer as variaveis de ambiente setadas
    from dotenv import load_dotenv
    load_dotenv()
    
    print("--- Testando Busca de Vagas ---")
    jobs = get_job_opportunities()
    print(f"Total de vagas: {len(jobs)}")
    
    print("\n--- Testando Busca de Leads ---")
    leads = get_business_leads()
    print(f"Total de leads: {len(leads)}")
