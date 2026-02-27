import json
from datetime import datetime
from core.config.settings import settings
from core.config.sites import SITES_MONITORADOS

# Imports dos Extratores
from core.extractors.pdf import PDFExtractor
from core.extractors.json_parser import JsonExtractor
from core.extractors.web import WebExtractor
from core.extractors.events import EventScraper

# Imports de Apoio
from core.parsers.heuristicas_editais import AnalisadorSemantico
from core.notifications.email_service import NotificadorOutlook
from core.logger import get_logger
from core.cleaner import formatar_data_br, limpar_resumo_tecnico

logger = get_logger("Pipeline")

class Pipeline:
    def __init__(self):
        self.extractor_pdf = PDFExtractor()
        self.extractor_web = WebExtractor()
        self.extractor_json = JsonExtractor()
        self.parser = AnalisadorSemantico()
        self.notificador = NotificadorOutlook()

    # --- CARREGAMENTO DE CURADORIA ---
    def _carregar_curadoria_premios(self):
        arquivo = settings.CURATED_DIR / "descricoes.json"
        if arquivo.exists():
            with open(arquivo, 'r', encoding='utf-8') as f: return json.load(f)
        return {}

    def _carregar_curadoria_eventos(self):
        arquivo = settings.CURATED_DIR / "eventos_curadoria.json"
        if arquivo.exists():
            try:
                with open(arquivo, 'r', encoding='utf-8') as f: return json.load(f)
            except: return {}
        return {}

    def _limpar_titulo_auto(self, texto):
        if not texto: return "Edital Sem Título"
        limpo = str(texto).replace(".pdf", "").replace(".PDF", "")
        limpo = limpo.replace("_", " ").replace("-", " ")
        return " ".join(limpo.split()).title()

    # --- PROCESSAMENTO DE PREMIAÇÕES ---
    def _processar_premios(self):
        logger.info("--- 🏆 Iniciando Scan de Premiações ---")
        curadoria = self._carregar_curadoria_premios()
        resultados = []

        for pdf in settings.INPUT_PDFS.glob("*.pdf"):
            try:
                raw_text = self.extractor_pdf.extract(pdf)
                if raw_text:
                    edital = self.parser.processar(raw_text, pdf.name)

                    if edital.titulo == pdf.name:
                        edital.titulo = self._limpar_titulo_auto(pdf.name)

                    edital.resumo = limpar_resumo_tecnico(edital.resumo)

                    if pdf.name in curadoria:
                        override = curadoria[pdf.name]
                        if "titulo" in override: edital.titulo = override["titulo"]
                        if "resumo" in override: edital.resumo = override["resumo"]
                        if "link_fonte" in override: edital.link_fonte = override["link_fonte"]
                        if "data_fim" in override:
                            edital.data_inscricao_fim = override["data_fim"]
                            try:
                                dt = datetime.strptime(override["data_fim"], "%Y-%m-%d").date()
                                edital.status = "ABERTO" if dt > datetime.now().date() else "ENCERRADO"
                            except: pass

                    edital.data_inscricao_fim = formatar_data_br(edital.data_inscricao_fim)
                    resultados.append(edital.model_dump(mode='json'))
            except Exception as e: logger.error(f"Erro PDF {pdf}: {e}")

        for nome_site, url in SITES_MONITORADOS.items():
            try:
                raw_text = self.extractor_web.extract_text(url)
                if raw_text and len(raw_text) > 200:
                    edital = self.parser.processar(raw_text, nome_site)
                    if edital.titulo == nome_site: edital.titulo = self._limpar_titulo_auto(nome_site)

                    edital.resumo = limpar_resumo_tecnico(edital.resumo)

                    if nome_site in curadoria:
                        override = curadoria[nome_site]
                        if "titulo" in override: edital.titulo = override["titulo"]
                        if "resumo" in override: edital.resumo = override["resumo"]
                        if "data_fim" in override:
                             edital.data_inscricao_fim = override["data_fim"]
                             try:
                                dt = datetime.strptime(override["data_fim"], "%Y-%m-%d").date()
                                edital.status = "ABERTO" if dt > datetime.now().date() else "ENCERRADO"
                             except: pass

                    edital.link_fonte = url
                    edital.data_inscricao_fim = formatar_data_br(edital.data_inscricao_fim)
                    resultados.append(edital.model_dump(mode='json'))
            except Exception as e: logger.error(f"Erro Site {nome_site}: {e}")

        arquivo_final = settings.OUTPUT_JSON / "monitoramento_consolidado.json"
        with open(arquivo_final, "w", encoding="utf-8") as f:
            json.dump(resultados, f, indent=4, ensure_ascii=False)
        self.notificador.enviar_premios(resultados)

    # --- PROCESSAMENTO DE EVENTOS ---
    def _processar_eventos(self):
        logger.info("--- 📅 Iniciando Scan de Eventos ---")
        curadoria = self._carregar_curadoria_eventos()
        lista_final = []

        try:
            scraper = EventScraper()
            eventos_raw = scraper.run()

            for evento in eventos_raw:
                nome_chave = evento["nome"]
                if nome_chave in curadoria:
                    logger.info(f"   ✨ Aplicando curadoria em evento: {nome_chave}")
                    evento.update(curadoria[nome_chave])
                lista_final.append(evento)

            logger.info(f"   ✅ Processados {len(lista_final)} eventos.")

        except Exception as e:
            logger.error(f"Erro fatal ao processar eventos: {e}")

        arquivo_saida = settings.OUTPUT_JSON / "eventos_consolidado.json"
        try:
            with open(arquivo_saida, 'w', encoding='utf-8') as f:
                json.dump({"eventos": lista_final}, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Erro salvando JSON: {e}")

        if lista_final: self.notificador.enviar_eventos(lista_final)

    def run_full_scan(self):
        logger.info(">>> 🚀 INICIANDO PIPELINE COMPLETO <<<")
        self._processar_premios()
        self._processar_eventos()
