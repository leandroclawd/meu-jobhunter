import os
import time
import threading
from flask import Flask
from dotenv import load_dotenv
import pytz
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from src.search_engine import get_job_opportunities
from src.ai_agent import evaluate_job
from src.telegram_bot import send_jobs_report, send_telegram_message

load_dotenv()

app = Flask(__name__)

# Configuração do Fuso Horário de Manaus (UTC-4)
MANAUS_TZ = pytz.timezone('America/Manaus')

@app.route('/')
def health_check():
    # Endpoint extremamente leve para o UptimeRobot e Render
    return "OK", 200

@app.route('/run')
def manual_run():
    now_str = datetime.now(MANAUS_TZ).strftime('%H:%M:%S')
    print(f"\n[*] Disparo manual via URL às {now_str}")
    search_thread = threading.Thread(target=run_job_search)
    search_thread.start()
    return "Busca de vagas iniciada com sucesso!", 200

def run_job_search():
    try:
        now = datetime.now(MANAUS_TZ)
        print(f"\n--- Iniciando Job Hunter Bot às {now.strftime('%d/%m/%Y %H:%M')} (Manaus) ---")
        
        print("\n1. Buscando novas oportunidades...")
        jobs = get_job_opportunities()
        
        if not jobs:
            print("Nenhuma vaga encontrada ou erro na busca.")
            send_jobs_report([])
            return
            
        print(f"\n2. Avaliando {len(jobs)} vagas com o Gemini...")
        avaliacoes = []
        
        for i, job in enumerate(jobs):
            print(f"  Avaliando vaga {i+1}/{len(jobs)}: {job['url']}")
            resultado = evaluate_job(job['url'], job['text'])
            if resultado:
                avaliacoes.append(resultado)
            time.sleep(2)
            
        if avaliacoes:
            print(f"\n3. Enviando {len(avaliacoes)} resultados aprovados...")
            try:
                with open("vagas_encontradas.md", "a", encoding="utf-8") as f:
                    f.write(f"\n\n## Buscas de {now.strftime('%d/%m/%Y %H:%M')}\n\n")
                    for av in avaliacoes:
                        f.write(av + "\n\n")
            except Exception as e:
                print(f"Erro ao salvar arquivo MD: {e}")
            send_jobs_report(avaliacoes)
        else:
            print("\nNenhuma das vagas foi aprovada.")
            send_jobs_report([])
            
    except Exception as e:
        print(f"Erro crítico no run_job_search: {e}")

def start_scheduler():
    # Inicializa o scheduler com o fuso horário correto
    scheduler = BackgroundScheduler(timezone=MANAUS_TZ)
    
    # Agendamentos originais (Manaus Time)
    scheduler.add_job(run_job_search, 'cron', hour=8, minute=0, id='search_morning')
    scheduler.add_job(run_job_search, 'cron', hour=18, minute=0, id='search_evening')
    
    # TESTE PARA O USUÁRIO: 20:00 de hoje (Manaus)
    scheduler.add_job(run_job_search, 'cron', hour=20, minute=0, id='search_test_20h')
    
    scheduler.start()
    
    # Log dos próximos passos
    print("\n[*] Scheduler iniciado (Fuso: America/Manaus)")
    for job in scheduler.get_jobs():
        print(f"    - Tarefa '{job.id}': Próxima execução em {job.next_run_time}")

    # Notificação tardia (após o boot do servidor principal)
    def notify_start():
        time.sleep(10) # Aguarda o servidor estabilizar
        send_telegram_message("🤖 **Job Hunter Bot** inicializado!\nFuso: Manaus (UTC-4)\nBuscas: 08:00, 18:00 e Teste 20:00.")
    
    threading.Thread(target=notify_start, daemon=True).start()

def init_bot():
    print("Validando variáveis de ambiente...")
    required = ["TELEGRAM_TOKEN", "TELEGRAM_CHAT_ID", "GEMINI_API_KEY"]
    missing = [env for env in required if not os.getenv(env)]
    
    if missing:
        print(f"Aviso: Variáveis faltando: {', '.join(missing)}")
        if "GEMINI_API_KEY" in missing:
            return False
            
    # Inicia o scheduler
    start_scheduler()
    return True

# Inicialização
if init_bot():
    print("[*] Bot pronto.")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

