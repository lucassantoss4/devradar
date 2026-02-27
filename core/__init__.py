import sys
import os
from flask import Flask

def create_app():
    # --- CORREÇÃO DE CAMINHO ---
    # Pega o caminho da pasta onde este arquivo está (__file__)
    # E sobe um nível ('..') para chegar na raiz 'devradar'
    base_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(base_dir, '..'))
    
    # Se a raiz não estiver no sistema de busca do Python, adiciona ela
    if root_dir not in sys.path:
        sys.path.insert(0, root_dir)
    # ---------------------------

    app = Flask(__name__)
    
    # Agora o Python consegue encontrar o 'core'
    from .routes import main_bp
    app.register_blueprint(main_bp)
    
    return app