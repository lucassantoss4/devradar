from flask import Blueprint, render_template, jsonify, request
from core.config.settings import settings
from core.pipeline import Pipeline
import json
import threading
import os
from functools import wraps
from core.notifications.automation_service import AutomationService
from datetime import datetime, date

main_bp = Blueprint('main', __name__)

# Habilita o trigger manual via dashboard apenas se a variável de ambiente estiver ativa.
# Em produção (Docker + Kestra), deixe esta variável INDEFINIDA ou False.
MANUAL_TRIGGER_ENABLED = os.getenv("ENABLE_MANUAL_TRIGGER", "false").lower() == "true"

# --- MAPA DE IMAGENS ---
LOGOS_MAP = {
    "aevo": "/static/images/aevo.jpg",
    "valor": "/static/images/valor-inovacao-2025_Final_imagem.avif",
    "premio inovacao": "/static/images/premio-inovacao.png", 
    "inovadora": "https://www.premioempresainovadora.com.br/wp-content/themes/premioei2024/images/logo.webp",
    "totvs": "https://premio.totvs.com/totvs-logo.svg",
    "open": "https://www.openstartups.net/site/ranking/images/logo-top.svg",
    "startups": "https://www.openstartups.net/site/ranking/images/logo-top.svg",
    "it forum": "/static/images/it-forum.png",
    "it midia": "/static/images/it-forum.png",
    "inovativos": "https://inovativos.com.br/premio/wp-content/uploads/2022/05/simbolo24.png",
    "best performance": "/static/images/premio_best_performance.png",
    "nacional de inovacao": "https://www.openstartups.net/site/ranking/images/logo-top.svg",
    "nacional de inovação": "https://www.openstartups.net/site/ranking/images/logo-top.svg",
    "intraempreendedorismo": "/static/images/aevo.jpg"
}

LOGO_DEFAULT = "/static/images/default.png"

def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-KEY')
        if api_key and api_key == settings.API_KEY:
            return f(*args, **kwargs)
        return jsonify({"error": "Unauthorized"}), 401
    return decorated

def carregar_dados():
    arquivo = settings.OUTPUT_JSON / "monitoramento_consolidado.json"
    dados = []
    if arquivo.exists():
        try:
            with open(arquivo, 'r', encoding='utf-8') as f:
                dados = json.load(f)
        except Exception as e:
            print(f"Erro JSON: {e}")

    for item in dados:
        titulo_lower = item.get('titulo', '').lower()
        item['logo_bg'] = LOGO_DEFAULT 
        for chave, url in LOGOS_MAP.items():
            if chave.lower() in titulo_lower:
                item['logo_bg'] = url
                break
    return dados

def carregar_eventos_tech():
    arquivo = settings.OUTPUT_JSON / "eventos_consolidado.json"
    if not arquivo.exists():
        arquivo = settings.DATA_DIR / "eventos" / "eventos.json"

    if arquivo.exists():
        try:
            with open(arquivo, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("eventos", [])
        except Exception as e:
            print(f"Erro ao ler eventos: {e}")
            return []
    return []

def preparar_timeline(premios, eventos):
    timeline = []
    hoje = date.today()
    
    def parse_data_iso(data_str):
        if not data_str: return None
        try:
            return datetime.strptime(data_str, "%Y-%m-%d").date()
        except: return None

    for p in premios:
        dt = None
        try:
            dt = datetime.strptime(p.get("data_inscricao_fim"), "%d/%m/%Y").date()
        except: pass
        
        dias_restantes = (dt - hoje).days if dt else 9999
        
        timeline.append({
            "tipo": "premio",
            "data_obj": dt,
            "data_display": p.get("data_inscricao_fim"),
            "titulo": p.get("titulo"),
            "subtitulo": "Prazo de Inscrição",
            "tag": p.get("custo"),
            "status": "PASSADO" if dt and dt < hoje else "FUTURO",
            "dias_restantes": dias_restantes,
            "link": p.get("link_fonte")
        })

    for e in eventos:
        data_str = e.get("data_inicio") 
        dt = parse_data_iso(data_str)
        dias_restantes = (dt - hoje).days if dt else 9999
        data_display = dt.strftime("%d/%m/%Y") if dt else "A Definir"

        timeline.append({
            "tipo": "evento",
            "data_obj": dt,
            "data_display": data_display,
            "titulo": e.get("nome"),
            "subtitulo": e.get("localizacao", {}).get("cidade", "Local N/A"),
            "tag": e.get("custo"),
            "status": "PASSADO" if dt and dt < hoje else "FUTURO",
            "dias_restantes": dias_restantes,
            "link": e.get("link")
        })

    def sort_key(item):
        if item['status'] == 'PASSADO': return (3, item['data_obj'] or date.max)
        if item['data_obj'] is None: return (2, 9999)
        return (1, item['dias_restantes'])

    timeline.sort(key=sort_key)
    
    meses_map = {1:'JAN', 2:'FEV', 3:'MAR', 4:'ABR', 5:'MAI', 6:'JUN', 7:'JUL', 8:'AGO', 9:'SET', 10:'OUT', 11:'NOV', 12:'DEZ'}
    for item in timeline:
        if item['status'] == 'PASSADO': item['grupo_mes'] = "HISTÓRICO"
        elif item['data_obj']: item['grupo_mes'] = f"{meses_map[item['data_obj'].month]} {item['data_obj'].year}"
        else: item['grupo_mes'] = "A DEFINIR"
            
    return timeline

@main_bp.route('/')
def dashboard():
    dados_premios = carregar_dados()
    dados_eventos = carregar_eventos_tech()
    dados_timeline = preparar_timeline(dados_premios, dados_eventos)
    
    return render_template(
        'dashboard.html', 
        oportunidades=dados_premios, 
        eventos=dados_eventos,
        timeline=dados_timeline
    )

@main_bp.route('/api/dados')
def api_dados():
    return jsonify(carregar_dados())

@main_bp.route('/api/run-pipeline', methods=['POST'])
def run_pipeline():
    """Trigger manual do pipeline. Habilite com ENABLE_MANUAL_TRIGGER=true (apenas dev)."""
    if not MANUAL_TRIGGER_ENABLED:
        return jsonify({
            "status": "disabled",
            "message": "Trigger manual desabilitado em produção. Use o Kestra para agendar o worker."
        }), 403

    def _executar():
        pipe = Pipeline()
        pipe.run_full_scan()

    threading.Thread(target=_executar, daemon=True).start()
    return jsonify({"status": "success", "message": "Pipeline iniciado em background."})

@main_bp.route('/api/v1/automation/data', methods=['GET'])
@require_api_key
def get_automation_data():
    """Endpoint para o Power Automate coletar dados filtrados."""
    try:
        data = AutomationService.get_urgent_data()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500