import re
from datetime import datetime
from core.parsers.schema_validator import EventSchemaValidator

class AnalisadorEventos:
    def __init__(self):
        self.validator = EventSchemaValidator()
        self.meses = {
            'janeiro': '01', 'fevereiro': '02', 'março': '03', 'marco': '03',
            'abril': '04', 'maio': '05', 'junho': '06', 'julho': '07',
            'agosto': '08', 'setembro': '09', 'outubro': '10', 'novembro': '11', 'dezembro': '12'
        }

    def processar(self, texto_bruto, nome_evento, url_fonte):
        texto_lower = texto_bruto.lower()
        
        # --- 1. DATA (Lógica Melhorada) ---
        data_encontrada = None
        
        # Tentativa A: Formato Numérico (dd/mm/aaaa)
        match_num = re.search(r'(\d{1,2})[\/\.](\d{1,2})[\/\.](\d{4})', texto_lower)
        if match_num:
            data_encontrada = f"{match_num.group(1)}/{match_num.group(2)}/{match_num.group(3)}"
        
        # Tentativa B: Formato Extenso (25 de março de 2026)
        if not data_encontrada:
            # Procura por: dia + (opcional: e dia) + de + mes + (opcional: de) + ano
            match_ext = re.search(r'(\d{1,2})\s*(?:e\s*\d{1,2})?\s*de\s*([a-zç]+)\s*(?:de)?\s*(\d{4})', texto_lower)
            if match_ext:
                dia, mes_nome, ano = match_ext.groups()
                if mes_nome in self.meses:
                    data_encontrada = f"{dia}/{self.meses[mes_nome]}/{ano}"

        # --- 2. OUTRAS EXTRAÇÕES ---
        tem_ia = any(t in texto_lower for t in ["inteligência artificial", "ai", "ia", "generative", "gpt"])
        
        custo = "A Confirmar"
        if any(x in texto_lower for x in ["compre", "ingresso", "lote", "investimento", "r$"]):
            custo = "Pago"
        elif any(x in texto_lower for x in ["gratuito", "free", "0800", "entrada franca"]):
            custo = "Gratuito"

        local_raw = "São Paulo" # Default seguro para eventos Tech BR
        if "online" in texto_lower or "transmissão" in texto_lower: 
            local_raw = "Online"
        elif "rio de janeiro" in texto_lower:
            local_raw = "Rio de Janeiro"
        elif "florianópolis" in texto_lower:
            local_raw = "Florianópolis"
        
        areas = []
        if tem_ia: areas.append("Inteligência Artificial")
        if "inovação" in texto_lower or "inovacao" in texto_lower: areas.append("Inovação")
        if "indústria" in texto_lower or "industria" in texto_lower: areas.append("Indústria 4.0")

        # --- DADOS BRUTOS ---
        dados_brutos = {
            "nome": nome_evento,
            "data": data_encontrada,
            "local": local_raw,
            "regiao": "SP",
            "categoria": "Tecnologia",
            "area_foco": areas,
            "ia_foco_principal": tem_ia,
            "custo": custo,
            "publico_alvo": "Misto",
            "link": url_fonte
        }

        return self.validator.normalize(dados_brutos)