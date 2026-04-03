import os

def build_dashboard(jobs, output_path="painel_vagas.html"):
    unique_urls = list(set([j['url'] for j in jobs]))
    total_jobs = len(unique_urls)
    
    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Job Hunter - Vagas RH Manaus</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
        
        :root {{
            --bg-color: #0b0f19;
            --card-bg: rgba(17, 24, 39, 0.7);
            --border-color: rgba(255, 255, 255, 0.08);
            --text-main: #f8fafc;
            --text-secondary: #94a3b8;
            --accent: #3b82f6;
            --gradient: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: 'Outfit', sans-serif;
            background-color: var(--bg-color);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 4rem 1.5rem;
            line-height: 1.6;
            background-image: 
                radial-gradient(circle at 15% 50%, rgba(59, 130, 246, 0.08), transparent 25%),
                radial-gradient(circle at 85% 30%, rgba(139, 92, 246, 0.08), transparent 25%);
            background-attachment: fixed;
        }}

        header {{
            text-align: center;
            margin-bottom: 3.5rem;
            animation: fadeInDown 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
            opacity: 0;
        }}

        h1 {{
            font-size: 3rem;
            font-weight: 800;
            margin-bottom: 0.5rem;
            background: var(--gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-fill-color: transparent;
            letter-spacing: -0.02em;
        }}

        p.subtitle {{
            color: var(--text-secondary);
            font-size: 1.2rem;
            font-weight: 300;
        }}

        .container {{
            width: 100%;
            max-width: 850px;
            display: grid;
            gap: 1rem;
            animation: fadeInUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
            animation-delay: 0.2s;
            opacity: 0;
        }}

        .card {{
            background: var(--card-bg);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 1.25rem 1.75rem;
            transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
            position: relative;
            overflow: hidden;
            text-decoration: none;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}

        .card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 4px;
            height: 100%;
            background: var(--gradient);
            opacity: 0;
            transition: opacity 0.3s ease;
        }}

        .card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 20px 40px -15px rgba(0,0,0,0.5);
            border-color: rgba(255, 255, 255, 0.15);
            background: rgba(30, 41, 59, 0.8);
        }}

        .card:hover::before {{
            opacity: 1;
        }}

        .card-content {{
            flex-grow: 1;
            padding-right: 1.5rem;
        }}

        .job-title {{
            color: var(--text-main);
            font-weight: 600;
            font-size: 1.15rem;
            margin-bottom: 0.25rem;
            word-break: break-all;
            transition: color 0.3s ease;
        }}
        
        .card:hover .job-title {{
            color: #fff;
        }}

        .job-domain {{
            color: var(--text-secondary);
            font-size: 0.9rem;
            font-weight: 400;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        .job-domain::before {{
            content: '';
            display: inline-block;
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: var(--accent);
            opacity: 0.7;
        }}

        .btn-visit {{
            background: rgba(255,255,255,0.03);
            border: 1px solid var(--border-color);
            padding: 0.6rem 1.2rem;
            border-radius: 10px;
            color: var(--text-main);
            font-weight: 600;
            font-size: 0.95rem;
            transition: all 0.3s ease;
            white-space: nowrap;
        }}

        .card:hover .btn-visit {{
            background: var(--gradient);
            border-color: transparent;
            box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
            transform: scale(1.05);
        }}

        @keyframes fadeInUp {{
            from {{ opacity: 0; transform: translateY(30px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        @keyframes fadeInDown {{
            from {{ opacity: 0; transform: translateY(-30px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        .empty-state {{
            text-align: center;
            color: var(--text-secondary);
            padding: 4rem 2rem;
            background: var(--card-bg);
            border-radius: 16px;
            border: 1px solid var(--border-color);
        }}
    </style>
</head>
<body>
    <header>
        <h1>Job Hunter Board</h1>
        <p class="subtitle">Resultado da última busca: <b>{total_jobs} oportunidades em RH</b></p>
    </header>
    
    <div class="container">
"""
    
    try:
        from urllib.parse import urlparse
        
        if not unique_urls:
            html += """
        <div class="empty-state">
            <p>Nenhuma vaga foi encontrada na última varredura. Tente novamente no próximo ciclo.</p>
        </div>
"""
        else:
            for url in unique_urls:
                try:
                    domain = urlparse(url).netloc
                    domain = domain.replace('www.', '')
                except:
                    domain = "Site parceiro"
                    
                display_url = url
                if len(display_url) > 75:
                    display_url = display_url[:72] + '...'
                    
                html += f"""
        <a href="{url}" target="_blank" class="card">
            <div class="card-content">
                <div class="job-title">{display_url}</div>
                <div class="job-domain">{domain}</div>
            </div>
            <div class="btn-visit">Ver Vaga</div>
        </a>
"""
    except Exception as e:
        html += f"<p style='color:red;'>Erro ao compilar o painel: {e}</p>"

    html += """
    </div>
</body>
</html>
"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[*] Painel web gerado com sucesso: {output_path} ({total_jobs} vagas)")
