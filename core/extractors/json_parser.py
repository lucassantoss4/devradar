import json
from pathlib import Path
from core.extractors.base import BaseExtractor
from core.logger import get_logger

logger = get_logger("JsonExtractor")

class JsonExtractor(BaseExtractor):
    def extract(self, file_path: Path) -> str:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                dados = json.load(f)
            
            # Suporta diferentes formatos (Firecrawl ou PDFPlumber)
            if "data" in dados and "markdown" in dados["data"]:
                return dados["data"]["markdown"]
            elif "conteudo_completo" in dados:
                return dados["conteudo_completo"]
            
            return str(dados) # Fallback

        except Exception as e:
            logger.error(f"Erro ao ler JSON {file_path}: {e}")
            return ""