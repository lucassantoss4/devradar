import re
import uuid
from datetime import datetime, date
from collections import Counter
from core.json_schema import EditalSchema
from core.logger import get_logger

logger = get_logger("Heuristics")

class AnalisadorSemantico:
    def __init__(self):
        self.mapa_meses = {
            'janeiro': '01', 'fevereiro': '02', 'março': '03', 'marco': '03',
            'abril': '04', 'maio': '05', 'junho': '06', 'julho': '07',
            'agosto': '08', 'setembro': '09', 'outubro': '10', 'novembro': '11', 'dezembro': '12',
            'jan': '01', 'fev': '02', 'mar': '03', 'abr': '04', 'mai': '05', 'jun': '06',
            'jul': '07', 'ago': '08', 'set': '09', 'out': '10', 'nov': '11', 'dez': '12'
        }

    def _detectar_ano_documento(self, texto: str) -> int:
        ano_atual = datetime.now().year
        anos_encontrados = re.findall(r"(202\d)", texto)
        if not anos_encontrados:
            return ano_atual
        contagem = Counter(anos_encontrados)
        return int(contagem.most_common(1)[0][0])

    def _converter_data(self, data_str, ano_default):
        try:
            data_str = data_str.lower().strip().replace('.', '/')
            for mes_nome, mes_num in self.mapa_meses.items():
                if mes_nome in data_str:
                    data_str = data_str.replace(mes_nome, mes_num).replace(' de ', '/').replace(' ', '/')
            
            match_full = re.search(r"(\d{1,2}/\d{1,2}/)(\d{4})", data_str)
            if match_full:
                return datetime.strptime(f"{match_full.group(1)}{match_full.group(2)}", "%d/%m/%Y").date()

            match_short = re.search(r"(\d{1,2}/\d{1,2})(?!\d)", data_str)
            if match_short:
                data_completa = f"{match_short.group(1)}/{ano_default}"
                return datetime.strptime(data_completa, "%d/%m/%Y").date()
        except: pass
        return None

    def _limpar_markdown(self, texto: str) -> str:
        if "--- CONTEÚDO ---" in texto:
            try:
                _, corpo_real = texto.split("--- CONTEÚDO ---", 1)
                texto = corpo_real
            except ValueError: pass
        
        texto = re.sub(r"# [A-Z_]+:.*", "", texto)
        texto = re.sub(r"!\[.*?\]\(.*?\)", "", texto)
        texto = re.sub(r"\[([^\]]+)\]\(.*?\)", r"\1", texto)
        texto = re.sub(r"(\w+\s*[-|]\s*){3,}", "", texto)
        texto = re.sub(r"[#*`]", "", texto)
        texto = re.sub(r"\s+", " ", texto).strip()
        return texto

    def processar(self, texto: str, nome_arquivo: str) -> EditalSchema:
        # 1. Extração de Metadados do Extrator (Link e Título)
        match_titulo = re.search(r"# TÍTULO_IDENTIFICADO: (.*)", texto)
        titulo = match_titulo.group(1).strip() if match_titulo else nome_arquivo
        
        # --- AQUI ESTÁ A CORREÇÃO DO LINK ---
        match_fonte = re.search(r"# FONTE_ORIGEM: (.*)", texto)
        # Se achar o link no texto (veio do scraper), usa ele. Se não, fica vazio.
        link_fonte = match_fonte.group(1).strip() if match_fonte else None
        if link_fonte and "Arquivo Local" in link_fonte:
            link_fonte = None # Limpa se for marcador de PDF local
        # ------------------------------------

        ano_documento = self._detectar_ano_documento(texto)
        linhas = texto.split('\n')
        candidatas_datas = []
        
        for linha in linhas:
            linha_lower = linha.lower()
            matches = re.findall(r"(\d{1,2}/\d{1,2}(?:/\d{4})?)", linha)
            if not matches:
                matches = re.findall(r"(\d{1,2}\s+de\s+[a-zç]+\s*(?:de\s+\d{4})?)", linha_lower)
            
            if matches:
                for m in matches:
                    dt = self._converter_data(m, ano_documento)
                    if dt:
                        score = 0
                        if "inscrição" in linha_lower or "inscricao" in linha_lower: score += 10
                        if "até" in linha_lower: score += 5
                        if "cerimônia" in linha_lower: score -= 5
                        candidatas_datas.append((score, dt))

        data_fim = None
        if candidatas_datas:
            hoje = datetime.now().date()
            futuras = [(s, d) for s, d in candidatas_datas if d >= hoje]
            if futuras:
                futuras.sort(key=lambda x: (x[0], x[1]), reverse=True)
                data_fim = futuras[0][1]
            else:
                candidatas_datas.sort(key=lambda x: (x[0], x[1]), reverse=True)
                data_fim = candidatas_datas[0][1]

        match_eleg = re.search(r"(?i)(?:##|###|\*\*)\s*(?:Elegibilidade|Quem pode participar|Público[- ]alvo|Restrições)(.*?)(?:##|###|\n\n)", texto, re.DOTALL)
        elegibilidade = match_eleg.group(1).strip()[:150] + "..." if match_eleg else "Não Identificada"
        if "startup" in texto.lower(): elegibilidade = "Foco em Startups/Tech"

        status = "ABERTO" if data_fim and data_fim >= datetime.now().date() else "ENCERRADO"
        custo = "Gratuito" if any(x in texto.lower() for x in ["gratuito", "isento", "sem custo"]) else "Sob Consulta"

        texto_limpo = self._limpar_markdown(texto)
        resumo_final = texto_limpo[:200]
        if resumo_final.rfind(' ') > 0:
            resumo_final = resumo_final[:resumo_final.rfind(' ')] + "..."

        return EditalSchema(
            id=str(uuid.uuid4())[:8],
            arquivo_origem=nome_arquivo,
            titulo=titulo,
            resumo=resumo_final,
            data_inscricao_fim=data_fim,
            status=status,
            custo=custo,
            elegibilidade=elegibilidade,
            link_fonte=link_fonte, # Agora passa o link real!
            processado_em=datetime.now().isoformat(),
            metodo_extracao="Híbrido v5 (Links)"
        )