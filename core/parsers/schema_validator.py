import re
from datetime import datetime

class EventSchemaValidator:
    """
    Padroniza eventos e remove termos técnicos como 'a_confirmar'.
    """

    DEFAULTS = {
        "localizacao": {"cidade": "São Paulo", "estado": "SP", "formato": "Presencial"},
        "categoria": "Tecnologia",
        "areas_foco": ["Tecnologia", "Inovação"],
        "ia_foco_principal": False,
        "custo": "A Confirmar",
        "publico_alvo": "Misto"
    }

    def normalize(self, dados_brutos):
        evento = {}

        # 1. NOME
        evento["nome"] = dados_brutos.get("nome", "Evento Desconhecido")

        # 2. DATA (Converte para ISO YYYY-MM-DD para o sistema)
        # O Frontend vai formatar de volta para BR
        raw_date = dados_brutos.get("data")
        evento["data_inicio"] = self._parse_date(raw_date)
        
        if evento["data_inicio"]:
            evento["data_status"] = "confirmada"
        else:
            evento["data_status"] = "a_confirmar" # Mantém snake_case só para lógica interna (cor do badge)

        # 3. LOCALIZAÇÃO
        raw_local = dados_brutos.get("local", "")
        evento["localizacao"] = self._parse_location(raw_local, dados_brutos.get("regiao"))

        # 4. CATEGORIA & ÁREAS
        evento["categoria"] = self._map_category(dados_brutos.get("categoria"))
        evento["areas_foco"] = self._map_areas(dados_brutos.get("area_foco"))

        # 5. IA
        evento["ia_foco_principal"] = bool(dados_brutos.get("ia_foco_principal"))

        # 6. CUSTO & PÚBLICO (Texto Limpo)
        raw_custo = str(dados_brutos.get("custo", "")).lower()
        if "grat" in raw_custo or "free" in raw_custo: evento["custo"] = "Gratuito"
        elif "pago" in raw_custo or "lote" in raw_custo: evento["custo"] = "Pago"
        else: evento["custo"] = "A Confirmar"

        raw_publico = str(dados_brutos.get("publico_alvo", "")).lower()
        if "tec" in raw_publico: evento["publico_alvo"] = "Técnico"
        elif "exec" in raw_publico: evento["publico_alvo"] = "Executivo"
        else: evento["publico_alvo"] = "Misto"

        # 7. LINK
        evento["link"] = dados_brutos.get("link", "")

        return evento

    def _parse_date(self, date_str):
        if not date_str or "confirmar" in str(date_str).lower(): return None
        try:
            # Tenta DD/MM/YYYY
            dt = datetime.strptime(str(date_str).strip(), "%d/%m/%Y")
            return dt.strftime("%Y-%m-%d")
        except: return None

    def _parse_location(self, local_str, regiao_str):
        loc = self.DEFAULTS["localizacao"].copy()
        texto = (str(local_str) + " " + str(regiao_str)).lower()
        
        if "online" in texto:
            loc.update({"formato": "Online", "cidade": "Online", "estado": "BR"})
            return loc

        if "paulo" in texto: loc.update({"cidade": "São Paulo", "estado": "SP"})
        elif "rio" in texto: loc.update({"cidade": "Rio de Janeiro", "estado": "RJ"})
        elif "florian" in texto: loc.update({"cidade": "Florianópolis", "estado": "SC"})
        elif "brasilia" in texto: loc.update({"cidade": "Brasília", "estado": "DF"})
        
        if local_str and local_str not in ["Verificar Site", "Online"]:
            loc["local"] = local_str
        return loc

    def _map_category(self, cat_raw):
        cat = str(cat_raw).lower()
        if "marketing" in cat: return "Marketing & Vendas"
        if "cloud" in cat: return "Cloud & DevOps"
        if "dados" in cat: return "Dados & Analytics"
        return "Tecnologia"

    def _map_areas(self, areas_raw):
        validas = ["Inteligência Artificial", "Cloud", "DevOps", "Marketing", "Vendas", "Dados", "Inovação", "Indústria 4.0"]
        if not areas_raw or not isinstance(areas_raw, list): return ["Inovação"]
        
        final = []
        for a in areas_raw:
            for v in validas:
                if a.lower() in v.lower() or v.lower() in a.lower():
                    if v not in final: final.append(v)
        return final if final else ["Tecnologia"]