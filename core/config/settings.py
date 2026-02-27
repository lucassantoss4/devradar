import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env
load_dotenv()

class Settings:
    # Define a raiz do projeto (devradar)
    # __file__ = settings.py
    # parent = config
    # parent.parent = core
    # parent.parent.parent = devradar (RAIZ)
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    
    # --- CAMINHOS DE DADOS ---
    DATA_DIR = BASE_DIR / "data"
    
    # Entradas
    INPUT_PDFS = DATA_DIR / "entrada_pdfs"
    INPUT_JSON = DATA_DIR / "entrada_json"
    
    # Saídas e Logs
    OUTPUT_JSON = DATA_DIR / "saida_json"
    LOGS_DIR = DATA_DIR / "logs"
    
    # Curadoria Manual
    CURATED_DIR = DATA_DIR / "curadoria"
    
    # --- CONFIGURAÇÃO DE E-MAIL ---
    EMAIL_TO = os.getenv("EMAIL_DESTINATARIOS", "")
    EMAIL_CC = os.getenv("EMAIL_COPIA", "")
    
    # --- SEGURANÇA E DEPLOY ---
    SECRET_KEY = os.getenv("SECRET_KEY", "")
    API_KEY = os.getenv("API_KEY", "")  # Protege endpoints de automação — obrigatório em produção
    
    # --- POWER AUTOMATE ---
    POWER_AUTOMATE_URL = os.getenv("POWER_AUTOMATE_WEBHOOK_URL", "")
    
    APP_NAME = "DevRadar"
    
    def setup_dirs(self):
        """Cria as pastas se não existirem"""
        pastas = [
            self.INPUT_PDFS, self.INPUT_JSON, 
            self.OUTPUT_JSON, self.LOGS_DIR, 
            self.CURATED_DIR
        ]
        for path in pastas:
            path.mkdir(parents=True, exist_ok=True)

# --- AQUI ESTAVA O ERRO ---
# Precisamos criar a instância da classe e chamá-la de 'settings'
# para que o outro arquivo consiga importar "from ... import settings"
settings = Settings()
settings.setup_dirs()