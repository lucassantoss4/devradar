import requests
from bs4 import BeautifulSoup
import urllib3
from core.logger import get_logger

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logger = get_logger("WebExtractor")

class WebExtractor:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def extract_text(self, url):
        """Acessa URL e retorna texto limpo (Markdown style)"""
        try:
            logger.info(f"🌐 Acessando: {url}")
            response = requests.get(url, headers=self.headers, timeout=15, verify=False)
            
            if response.status_code != 200:
                logger.error(f"❌ Erro HTTP {response.status_code} em {url}")
                return ""

            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Limpeza
            for tag in soup(["script", "style", "nav", "footer", "iframe", "noscript"]):
                tag.extract()

            text = soup.get_text(separator='\n')
            
            # Remove linhas vazias excessivas
            lines = (line.strip() for line in text.splitlines())
            clean_text = '\n'.join(chunk for chunk in lines if chunk)

            return f"# Fonte: Web Scraping\n# URL: {url}\n\n{clean_text}"

        except Exception as e:
            logger.error(f"❌ Erro de conexão em {url}: {e}")
            return ""