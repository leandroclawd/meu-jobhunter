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
            --color-new: #10b981;
            --color-tracked: #f59e0b;
            --color-discard: #ef4444;
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

        .card:hover::before {{ opacity: 1; }}

        /* Status esteticos baseados nas tags */
        .card.new-job {{ border-left: 4px solid var(--color-new); }}
        .card.new-job::before {{ background: var(--color-new); border-color: var(--color-new); opacity: 1; }}
        
        .card.tracked {{ border-color: var(--color-tracked); box-shadow: 0 0 15px rgba(245, 158, 11, 0.15); }}
        .card.tracked::before {{ background: var(--color-tracked); opacity: 1; }}

        .card-content {{
            flex-grow: 1;
            padding-right: 1.5rem;
        }}

        .job-title-link {{
            text-decoration: none;
            color: var(--text-main);
            display: inline-block;
        }}

        .job-title {{
            font-weight: 600;
            font-size: 1.15rem;
            margin-bottom: 0.25rem;
            word-break: break-all;
            transition: color 0.3s ease;
        }}
        
        .card:hover .job-title {{ color: #fff; }}

        .job-domain {{
            color: var(--text-secondary);
            font-size: 0.9rem;
            font-weight: 400;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            flex-wrap: wrap;
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

        /* Botoes e Acoes */
        .actions {{
            display: flex;
            gap: 0.6rem;
            flex-wrap: nowrap;
        }}

        .btn-action {{
            background: rgba(255,255,255,0.03);
            border: 1px solid var(--border-color);
            padding: 0.6rem 1rem;
            border-radius: 10px;
            color: var(--text-main);
            font-weight: 600;
            font-size: 0.85rem;
            transition: all 0.3s ease;
            white-space: nowrap;
            cursor: pointer;
            text-decoration: none;
        }}
        
        .btn-visit {{ color: #fff; }}
        .card:hover .btn-visit {{
            background: var(--gradient);
            border-color: transparent;
            box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
        }}

        .btn-discard:hover {{ background: var(--color-discard); border-color: transparent; }}
        .btn-track:hover {{ background: var(--color-tracked); border-color: transparent; }}
        .btn-tracked-active {{ background: var(--color-tracked); border-color: transparent; }}

        /* Badges */
        .badge-new {{ background: var(--color-new); color: #fff; padding: 2px 6px; border-radius: 4px; font-size: 0.7rem; font-weight: 800; letter-spacing: 0.05em; }}
        .badge-tracked {{ background: var(--color-tracked); color: #fff; padding: 2px 6px; border-radius: 4px; font-size: 0.7rem; font-weight: 800; letter-spacing: 0.05em; }}

        .btn-update {{
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid var(--border-color);
            padding: 0.6rem 1.2rem;
            border-radius: 8px;
            color: var(--text-main);
            font-weight: 600;
            font-size: 0.9rem;
            cursor: pointer;
            transition: all 0.3s;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            margin-top: 1rem;
        }}
        .btn-update:hover {{
            background: var(--gradient);
            border-color: transparent;
        }}
        .btn-update:active {{ transform: scale(0.95); }}
        
        #toast-notification {{
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: var(--gradient);
            color: #fff;
            padding: 1rem 1.5rem;
            border-radius: 12px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.5);
            transform: translateY(100px);
            opacity: 0;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            z-index: 999;
            font-weight: 600;
        }}
        #toast-notification.show {{
            transform: translateY(0);
            opacity: 1;
        }}

        @keyframes fadeInUp {{ from {{ opacity: 0; transform: translateY(30px); }} to {{ opacity: 1; transform: translateY(0); }} }}
        @keyframes fadeInDown {{ from {{ opacity: 0; transform: translateY(-30px); }} to {{ opacity: 1; transform: translateY(0); }} }}
        
        .empty-state {{ text-align: center; color: var(--text-secondary); padding: 4rem 2rem; background: var(--card-bg); border-radius: 16px; border: 1px solid var(--border-color); }}
        
        /* Stats dashboard */
        .stats {{ display: flex; gap: 2rem; justify-content: center; margin-bottom: 2rem; animation: fadeInDown 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards; opacity: 0; animation-delay: 0.1s; }}
        .stat-box {{ background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 12px; padding: 1rem 2rem; text-align: center; }}
        .stat-value {{ font-size: 2rem; font-weight: 800; background: var(--gradient); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
        .stat-label {{ font-size: 0.85rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.05em; margin-top: 0.2rem; }}

    </style>
</head>
<body>
    <header>
        <h1>Job Hunter Board</h1>
        <p class="subtitle">Resultado da última busca em Manaus/AM</p>
        <button class="btn-update" onclick="forceUpdate()">🔄 Buscar Novas Vagas Agora!</button>
    </header>
    
    <div class="stats" id="dashboard-stats">
        <div class="stat-box">
            <div class="stat-value" id="stat-total">{total_jobs}</div>
            <div class="stat-label">Vagas Listadas</div>
        </div>
        <div class="stat-box">
            <div class="stat-value" id="stat-novas" style="background: var(--color-new); -webkit-background-clip: text;">0</div>
            <div class="stat-label">Vagas Novas Hoje</div>
        </div>
        <div class="stat-box">
            <div class="stat-value" id="stat-acompanhando" style="background: var(--color-tracked); -webkit-background-clip: text;">0</div>
            <div class="stat-label">Acompanhando</div>
        </div>
    </div>
    
    <div class="container" id="cards-container">
"""
    
    try:
        from urllib.parse import urlparse
        
        if not unique_urls:
            html += """
        <div class="empty-state">
            <p>Nenhuma vaga foi encontrada na última varredura.</p>
        </div>
"""
        else:
            for i, url in enumerate(unique_urls):
                try:
                    domain = urlparse(url).netloc
                    domain = domain.replace('www.', '')
                except:
                    domain = "Site parceiro"
                    
                display_url = url
                if len(display_url) > 75:
                    display_url = display_url[:72] + '...'
                    
                html += f"""
        <div class="card" data-url="{url}" id="card-{i}">
            <div class="card-content">
                <a href="{url}" target="_blank" class="job-title-link">
                    <div class="job-title">{display_url}</div>
                </a>
                <div class="job-domain">{domain} <span class="badges-container"></span></div>
            </div>
            <div class="actions">
                <button class="btn-action btn-track" onclick="toggleTrack('{url}', 'card-{i}')">⭐ Seguir</button>
                <button class="btn-action btn-discard" onclick="discardJob('{url}', 'card-{i}')">🗑️ Ocultar</button>
                <a href="{url}" target="_blank" class="btn-action btn-visit">Ir pra Vaga</a>
            </div>
        </div>
"""
    except Exception as e:
        html += f"<p style='color:red;'>Erro ao compilar o painel: {e}</p>"

    html += """
    </div>

    <div id="toast-notification">A caçada começou! Atualize a página em 1 minutinho. 🚀</div>

    <script>
    function forceUpdate() {
        let btn = document.querySelector('.btn-update');
        btn.innerText = '⏳ Robô trabalhando...';
        btn.style.opacity = '0.7';
        btn.disabled = true;
        
        fetch('/run')
            .then(res => {
                let toast = document.getElementById('toast-notification');
                toast.classList.add('show');
                setTimeout(() => { toast.classList.remove('show'); }, 6000);
            })
            .catch(err => console.error(err));
    }

    document.addEventListener("DOMContentLoaded", function() {
        let discarded = JSON.parse(localStorage.getItem('job_discarded') || '[]');
        let tracked = JSON.parse(localStorage.getItem('job_tracked') || '[]');
        let seen = JSON.parse(localStorage.getItem('job_seen') || '[]');
        
        let newCount = 0;
        let trackedCount = 0;
        let visibleCount = 0;
        
        document.querySelectorAll('.card').forEach(card => {
            let url = card.getAttribute('data-url');
            
            // Remocao das descartadas
            if (discarded.includes(url)) {
                card.style.display = 'none';
                return; // Pula o resto da analise pra esse card
            }
            
            visibleCount++;
            let badges = card.querySelector('.badges-container');
            
            // Vagas acompanhadas
            if (tracked.includes(url)) {
                card.classList.add('tracked');
                let trackBtn = card.querySelector('.btn-track');
                trackBtn.innerText = '★ Remover';
                trackBtn.classList.add('btn-tracked-active');
                badges.innerHTML += '<span class="badge-tracked badge-node">SEGUINDO</span>';
                trackedCount++;
            }
            
            // Novas Vagas (Apenas marca como nova, salva no localstore no final do loop)
            if (!seen.includes(url)) {
                card.classList.add('new-job');
                badges.innerHTML += '<span class="badge-new badge-node">NOVA HOJE</span>';
                newCount++;
                seen.push(url);
            }
        });
        
        // Update stats
        document.getElementById('stat-total').innerText = visibleCount;
        document.getElementById('stat-novas').innerText = newCount;
        document.getElementById('stat-acompanhando').innerText = trackedCount;
        
        // Salva que vimos essas vagas hoje (evita duplicar "NOVA" eternamente)
        localStorage.setItem('job_seen', JSON.stringify(seen));
    });
    
    function discardJob(url, cardId) {
        let discarded = JSON.parse(localStorage.getItem('job_discarded') || '[]');
        if (!discarded.includes(url)) {
            discarded.push(url);
            localStorage.setItem('job_discarded', JSON.stringify(discarded));
        }
        // Anima a saida
        let card = document.getElementById(cardId);
        card.style.opacity = '0';
        card.style.transform = 'translateX(50px)';
        setTimeout(() => {
            card.style.display = 'none';
            updateStats();
        }, 300);
    }
    
    function toggleTrack(url, cardId) {
        let tracked = JSON.parse(localStorage.getItem('job_tracked') || '[]');
        let card = document.getElementById(cardId);
        let trackBtn = card.querySelector('.btn-track');
        let badges = card.querySelector('.badges-container');
        
        if (tracked.includes(url)) {
            // Un-track
            tracked = tracked.filter(u => u !== url);
            localStorage.setItem('job_tracked', JSON.stringify(tracked));
            
            card.classList.remove('tracked');
            trackBtn.innerText = '⭐ Seguir';
            trackBtn.classList.remove('btn-tracked-active');
            let b = badges.querySelector('.badge-tracked');
            if (b) b.remove();
        } else {
            // Track
            tracked.push(url);
            localStorage.setItem('job_tracked', JSON.stringify(tracked));
            
            card.classList.add('tracked');
            trackBtn.innerText = '★ Remover';
            trackBtn.classList.add('btn-tracked-active');
            badges.innerHTML += '<span class="badge-tracked badge-node">SEGUINDO</span>';
        }
        updateStats();
    }
    
    function updateStats() {
        let tracked = JSON.parse(localStorage.getItem('job_tracked') || '[]');
        let discarded = JSON.parse(localStorage.getItem('job_discarded') || '[]');
        let allCards = document.querySelectorAll('.card');
        
        let visibleCount = 0;
        allCards.forEach(c => {
            if (c.style.display !== 'none') visibleCount++;
        });
        
        document.getElementById('stat-total').innerText = visibleCount;
        document.getElementById('stat-acompanhando').innerText = tracked.length;
    }
    </script>
</body>
</html>
"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[*] Painel web gerado com sucesso: {output_path} ({total_jobs} vagas)")
