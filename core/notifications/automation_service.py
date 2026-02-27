import json
from datetime import datetime, date
from core.config.settings import settings

class AutomationService:
    @staticmethod
    def get_urgent_data():
        """
        Coleta dados de premiações e eventos que precisam de atenção (ex: próximos 15 dias).
        Retorna um dicionário formatado para JSON.
        """
        hoje = date.today()
        
        # 1. Carregar Prêmios
        premios_file = settings.OUTPUT_JSON / "monitoramento_consolidado.json"
        premios_list = []
        if premios_file.exists():
            with open(premios_file, 'r', encoding='utf-8') as f:
                raw_premios = json.load(f)
                for p in raw_premios:
                    if p.get('status') != 'ABERTO': continue
                    try:
                        dt_fim = datetime.strptime(p['data_inscricao_fim'], "%d/%m/%Y").date()
                        dias = (dt_fim - hoje).days
                        if 0 <= dias <= 15: # Apenas os que vencem em 15 dias
                            p['dias_restantes'] = dias
                            premios_list.append(p)
                    except: pass
        
        # 2. Carregar Eventos
        eventos_file = settings.OUTPUT_JSON / "eventos_consolidado.json"
        eventos_list = []
        if eventos_file.exists():
            with open(eventos_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                raw_eventos = data.get("eventos", [])
                for e in raw_eventos:
                    try:
                        dt_inicio = datetime.strptime(e['data_inicio'], "%Y-%m-%d").date()
                        dias = (dt_inicio - hoje).days
                        if 0 <= dias <= 30: # Eventos nos próximos 30 dias
                            e['dias_para_evento'] = dias
                            eventos_list.append(e)
                    except: pass

        return {
            "timestamp": datetime.now().isoformat(),
            "resumo": {
                "total_premios_urgentes": len(premios_list),
                "total_eventos_proximos": len(eventos_list)
            },
            "premios": sorted(premios_list, key=lambda x: x.get('dias_restantes', 99)),
            "eventos": sorted(eventos_list, key=lambda x: x.get('dias_para_evento', 99))
        }
