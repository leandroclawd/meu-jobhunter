import os
import time
import schedule
import threading
from flask import Flask
from dotenv import load_dotenv
from src.search_engine import get_job_opportunities
from src.ai_agent import evaluate_job
from src.telegram_bot import send_jobs_report

load_dotenv()

app = Flask(__name__)

@app.route('/')
def health_check():
    return "Job Hunter Bot is running!", 200

def run_job_search():
    print(f"\n--- Iniciando Job Hunter Bot às {time.strftime('%H:%M')} ---")
    
    print("\n1. Buscando novas oportunidades nos sites...")
    jobs = get_job_opportunities()
    
    if not jobs:
        print("Nenhuma vaga encontrada ou erro na busca.")
        send_jobs_report([]) # Notifica o Telegram que a busca terminou (mesmo sem resultados)
        return
        
    print(f"\n2. Avaliando {len(jobs)} vagas com o Gemini...")
    avaliacoes = []
    
    for i, job in enumerate(jobs):
        print(f"  Avaliando vaga {i+1}/{len(jobs)}: {job['url']}")
        resultado = evaluate_job(job['url'], job['text'])
        
        if resultado:
            avaliacoes.append(resultado)
            
        time.sleep(2)  # Pausa pequena para evitar sobrecarregar a API do Gemini
        
    if avaliacoes:
        print(f"\n3. Salvando e enviando {len(avaliacoes)} resultados aprovados...")
        try:
            with open("vagas_encontradas.md", "a", encoding="utf-8") as f:
                f.write(f"\n\n## Buscas de {time.strftime('%d/%m/%Y %H:%M')}\n\n")
                for av in avaliacoes:
                    f.write(av + "\n\n")
            print("Salvo no relatório MD com sucesso.")
        except Exception as e:
            print(f"Erro ao salvar arquivo MD: {e}")
            
        # Envia pelo telegram
        send_jobs_report(avaliacoes)
    else:
        print("\nNenhuma das vagas de hoje foi aprovada pelo critério do agente.")
        send_jobs_report([]) # Também avisa se nenhuma foi aprovada pelo critério

def run_scheduler():
    print("\nConfigurando agendamento. O bot rodará 2 vezes ao dia (08:00 e 18:00).")
    
    # Notifica que o bot está ativo
    from src.telegram_bot import send_telegram_message
    send_telegram_message("🤖 **Job Hunter Bot** inicializado com sucesso na nuvem!")
    
    # Roda a primeira vez ao iniciar
    run_job_search()
    
    # Agenda para depois
    schedule.every().day.at("08:00").do(run_job_search)
    schedule.every().day.at("18:00").do(run_job_search)
    
    print("\n[*] Scheduler em modo de espera.")
    while True:
        schedule.run_pending()
        time.sleep(60)

def init_bot():
    print("Job Hunter Bot inicializado. Validando ambiente...")
    
    if not os.getenv("TELEGRAM_TOKEN"):
        print("Aviso: TELEGRAM_TOKEN não configurado!")
    if not os.getenv("TELEGRAM_CHAT_ID"):
        print("Aviso: TELEGRAM_CHAT_ID não configurado!")
    if not os.getenv("GEMINI_API_KEY"):
        print("Erro: GEMINI_API_KEY não encontrada!")
        return

    # Inicia o scheduler em uma thread separada
    print("\n[*] Iniciando agendador de tarefas em segundo plano...")
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()

# Inicializa o bot assim que o módulo for carregado (pelo Gunicorn ou localmente)
init_bot()

def main():
    # Inicia o servidor Flask localmente (apenas para desenvolvimento)
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    main()
