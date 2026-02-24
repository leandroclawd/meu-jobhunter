import os
import requests

def send_telegram_message(message):
    """
    Envia uma mensagem para o Telegram usando a API HTTP do bot.
    """
    token = os.getenv("TELEGRAM_TOKEN")
    # Para simplificar na v1, vamos pegar o chat_id do próprio token ou via variavel
    # No envio via telegram de bot para usuario, precisamos do Chat ID do usuario
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not token:
        print("Erro: TELEGRAM_TOKEN não configurado.")
        return False
        
    if not chat_id:
        print("Erro: TELEGRAM_CHAT_ID não configurado. Por favor, adicione o ID numérico do seu chat com o bot no .env")
        return False
        
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        print(f"[Telegram] Status: {response.status_code}, Resposta: {response.text}")
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"Erro ao enviar mensagem pro Telegram: {e}")
        return False
        
def send_jobs_report(avaliacoes):
    """
    Formata e envia as avaliações no Telegram.
    Divide em várias mensagens se ficar muito grande.
    """
    if not avaliacoes:
        send_telegram_message("🤖 Job Hunter: Nenhuma vaga aderente encontrada nesta busca.")
        return
        
    header = f"🚀 *Job Hunter Bot* - Encontrei {len(avaliacoes)} novas vagas aderentes!\n\n"
    
    # Junta as mensagens e corta se passar do limite do Telegram (4096 chars)
    # Para ser seguro, dividiremos cada vaga em uma mensagem se forem muitas
    
    send_telegram_message(header)
    
    for av in avaliacoes:
        # Tenta enviar cada avaliação
        sucesso = send_telegram_message(av)
        if not sucesso:
            # Fallback se a mensagem tiver formatação markdown quebrada
            payload = {
                "chat_id": os.getenv("TELEGRAM_CHAT_ID"),
                "text": av, # Sem parse_mode
            }
            requests.post(f"https://api.telegram.org/bot{os.getenv('TELEGRAM_TOKEN')}/sendMessage", json=payload)
    
    print("Relatório enviado com sucesso via Telegram!")
