import os
import webbrowser
from src.search_engine import get_job_opportunities, get_business_leads
from src.html_generator import build_dashboard

def main():
    print("====================================")
    print(" ROBÔ INICIADO: Buscando vagas...   ")
    print(" Isso pode levar cerca de 1 minuto. ")
    print("====================================")
    
    # 1. Faz a busca de vagas
    jobs = get_job_opportunities()
    
    # 2. Faz a busca de leads (notícias de expansão)
    print("\n[*] Buscando notícias de expansão empresarial...")
    leads = get_business_leads()
    
    if not jobs and not leads:
        print("\n[!] Nada encontrado no momento (vagas ou notícias).")
        build_dashboard([], []) 
    else:
        print(f"\n[*] Busca concluída! {len(jobs)} vagas e {len(leads)} notícias encontradas.")
        # 3. Gera o novo arquivo HTML no HD
        build_dashboard(jobs, leads)
    
    # 4. Abre o arquivo final diretamente no navegador
    html_path = 'file://' + os.path.realpath('painel_vagas.html')
    print(f"[*] Abrindo o navegador: {html_path}")
    try:
        webbrowser.open(html_path)
    except:
        print(f"[!] Não foi possível abrir o navegador automaticamente. Abra manualmente: {html_path}")
    
    print("\nFinalizado.")

if __name__ == "__main__":
    main()
