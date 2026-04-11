import os
import time
import threading
from flask import Flask, send_file, make_response, jsonify
from dotenv import load_dotenv
import pytz
from datetime import datetime

from src.search_engine import get_job_opportunities
from src.html_generator import build_dashboard

load_dotenv()

app = Flask(__name__)

# Configuração do Fuso Horário de Manaus (UTC-4)
MANAUS_TZ = pytz.timezone('America/Manaus')

# Flag global para indicar se a busca está rodando
IS_SEARCHING = False

@app.route('/')
@app.route('/ping')
def health_check():
    return "Bot is alive!", 200

@app.route('/vagas')
def painel_vagas():
    # Verifica se o arquivo existe antes de enviar
    if not os.path.exists('painel_vagas.html'):
        # Gera versão inicial vazia
        build_dashboard([])
        
    response = make_response(send_file('painel_vagas.html'))
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.route('/status')
def check_status():
    global IS_SEARCHING
    return jsonify({"is_searching": IS_SEARCHING})

@app.route('/run')
def manual_run():
    global IS_SEARCHING
    if IS_SEARCHING:
        return "Já existe uma busca em andamento.", 400
        
    now_str = datetime.now(MANAUS_TZ).strftime('%H:%M:%S')
    print(f"\n[*] Disparo manual via URL às {now_str}")
    search_thread = threading.Thread(target=run_job_search_task)
    search_thread.start()
    return "Busca de vagas iniciada com sucesso!", 200

def run_job_search_task():
    global IS_SEARCHING
    IS_SEARCHING = True
    try:
        now = datetime.now(MANAUS_TZ)
        print(f"\n--- Iniciando Busca Web às {now.strftime('%d/%m/%Y %H:%M')} (Manaus) ---")
        
        print("\n1. Buscando novas oportunidades...")
        jobs = get_job_opportunities()
        
        print(f"\n2. Atualizando o painel interativo na web com {len(jobs)} vagas...")
        build_dashboard(jobs)
        print("\n[*] Painel atualizado.")
            
    except Exception as e:
        print(f"Erro crítico no run_job_search: {e}")
    finally:
        IS_SEARCHING = False

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

