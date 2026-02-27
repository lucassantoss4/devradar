# =============================================================================
# DevRadar — Dockerfile
# =============================================================================
# Imagem base: Python 3.11 slim (Debian Bookworm)
# Otimizado para: Gunicorn (web) e worker.py (pipeline)
# =============================================================================

FROM python:3.11-slim-bookworm AS base

# --- Dependências de sistema para OCR (docling/PyMuPDF/libGL) ---
RUN apt-get update && apt-get install -y --no-install-recommends \
    # OpenCV / libGL (usado por docling internamente)
    libgl1 \
    libglib2.0-0 \
    # Processamento de PDF
    libmupdf-dev \
    # Playwright / Chromium (web scraping headless)
    chromium \
    chromium-driver \
    # Utilitários
    curl \
    && rm -rf /var/lib/apt/lists/*

# Garante que Playwright use o Chromium do sistema (evita segundo download)
ENV PLAYWRIGHT_BROWSERS_PATH=/usr/bin
ENV CHROMIUM_FLAGS="--no-sandbox --headless"

# --- Configuração do usuário (não-root por segurança) ---
RUN useradd --create-home --shell /bin/bash devradar
WORKDIR /app

# --- Instalação de dependências Python ---
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    # Instala o browser para o playwright (Chromium já no sistema, mas playwright precisa registrar)
    && playwright install chromium --with-deps || true

# --- Cópia do código-fonte ---
COPY --chown=devradar:devradar . .

# --- Cria as pastas de dados necessárias ---
RUN mkdir -p data/entrada_pdfs data/entrada_json data/saida_json data/logs data/curadoria

# --- Usuário não-root ---
USER devradar

# --- Variáveis de ambiente padrão ---
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV FLASK_ENV=production

# --- Porta exposta ---
EXPOSE 5000

# --- Ponto de entrada padrão: servidor web ---
# Para rodar o worker: docker run devradar python worker.py
CMD ["gunicorn", \
     "--bind", "0.0.0.0:5000", \
     "--workers", "2", \
     "--timeout", "120", \
     "--log-level", "info", \
     "--access-logfile", "-", \
     "run_web:app"]
