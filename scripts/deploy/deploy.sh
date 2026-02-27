#!/bin/bash

# --- CONFIGURAÇÕES ---
APP_NAME="inova-monitoring"
APP_DIR="/var/www/$APP_NAME"
VENV_PATH="$APP_DIR/venv"

echo "🚢 Iniciando Deploy de $APP_NAME..."

cd $APP_DIR

# 1. Puxar as últimas alterações (Git)
# git pull origin main

# 2. Ativar Ambiente Virtual e Atualizar Dependências
source $VENV_PATH/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 3. Rodar Checklist de Verificação (Opcional)
# python .agent/scripts/checklist.py .

# 4. Reiniciar o serviço Systemd
sudo systemctl restart $APP_NAME

echo "✅ Deploy finalizado com sucesso às $(date)"
echo "📡 Verifique os logs com: journalctl -u $APP_NAME -f"
