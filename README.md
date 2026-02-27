<p align="center">
  <h1 align="center">📡 DevRadar</h1>
  <p align="center">
    <strong>Market Intelligence Platform — OCR · Web Scraping · Flask Dashboard</strong>

---

## O que é o DevRadar?

DevRadar é uma plataforma de **monitoramento automatizado de oportunidades de inovação** — prêmios, editais e eventos tech — usando OCR (PDF), Web Scraping e um Dashboard interativo em Flask.

O sistema extrai, analisa e consolida informações de múltiplas fontes (PDFs, websites, APIs) em um painel visual com timeline, filtros e notificações por e-mail.

---

  </p>
  <p align="center">
    <img src="https://img.shields.io/badge/python-3.11+-blue?logo=python&logoColor=white" alt="Python">
    <img src="https://img.shields.io/badge/flask-3.0-green?logo=flask&logoColor=white" alt="Flask">
    <img src="https://img.shields.io/badge/docker-ready-2496ED?logo=docker&logoColor=white" alt="Docker">
    <img src="https://img.shields.io/badge/license-MIT-yellow" alt="License">
  </p>
</p>



## Arquitetura

```
                    ┌─────────────┐
                    │    Kestra   │  (agendador externo)
                    └──────┬──────┘
                           │ cron
                           ▼
┌──────────────┐    ┌─────────────┐    ┌─────────────┐
│  run_web.py  │    │  worker.py  │───▶│    data/    │
│  (Gunicorn)  │    │  Pipeline   │    │  saida_json │
│  Dashboard   │    └─────────────┘    └──────┬──────┘
└──────────────┘                              │ lê
       ▲ ◄────────────────────────────────────┘
       │ HTTP
    Browser
```

| Componente | Arquivo | Papel |
|------------|---------|-------|
| **Web Server** | `run_web.py` | Dashboard Flask + API REST (Gunicorn-ready) |
| **Worker** | `worker.py` | Pipeline CLI — roda e morre (Kestra) |
| **Extractors** | `core/extractors/` | PDF (docling), Web (crawl4ai), JSON, Events |
| **Parsers** | `core/parsers/` | Heurísticas de análise semântica |
| **Notifications** | `core/notifications/` | E-mail (Outlook COM) + Webhook (Power Automate) |

---

## Estrutura de Pastas

```
devradar/
├── run_web.py              # Entry point: Flask server
├── worker.py               # Entry point: Pipeline CLI
├── Dockerfile              # Imagem Docker otimizada
├── requirements.txt
├── .env.example            # Template de variáveis de ambiente
│
├── app/                    # Flask app (routes, templates, static)
│   ├── routes.py
│   ├── templates/
│   └── static/
│
├── core/                   # Lógica de negócio
│   ├── config/             # Settings, sites monitorados
│   ├── extractors/         # PDF, Web, Events, JSON
│   ├── parsers/            # Heurísticas, schema validator
│   ├── notifications/      # Email, webhook
│   ├── pipeline.py         # Orquestrador do scan completo
│   ├── logger.py
│   ├── cleaner.py
│   └── json_schema.py
│
├── data/                   # Runtime (gitignored)
│   ├── entrada_pdfs/
│   ├── saida_json/
│   └── logs/
│
└── scripts/deploy/         # Gunicorn, Nginx, setup
```

---

## Quick Start

### 1. Clone e configure

```bash
git clone https://github.com/lucassantoss4/devradar.git
cd devradar
cp .env.example .env
# Edite .env com seus valores
```

### 2. Instale dependências

```bash
python -m venv .venv
source .venv/bin/activate    # Linux/Mac
# .venv\Scripts\activate     # Windows
pip install -r requirements.txt
playwright install chromium
```

### 3. Rode o Dashboard

```bash
python run_web.py
# → http://localhost:5000
```

### 4. Rode o Pipeline manualmente

```bash
python worker.py                # Scan completo
python worker.py --premios      # Apenas premiações
python worker.py --eventos      # Apenas eventos
```

---

## Docker

```bash
# Build
docker build -t devradar .

# Web server (fica ativo)
docker run -d -p 5000:5000 --env-file .env --name devradar-web devradar

# Worker (disparo único)
docker run --rm --env-file .env devradar python worker.py
```

---

## Variáveis de Ambiente

| Variável | Descrição | Obrigatória |
|----------|-----------|:-----------:|
| `SECRET_KEY` | Chave secreta do Flask | ✅ |
| `API_KEY` | Autenticação dos endpoints de automação | ✅ |
| `EMAIL_DESTINATARIOS` | E-mail(s) para relatórios (separar com `;`) | ✅ |
| `EMAIL_COPIA` | E-mail(s) em CC | ❌ |
| `POWER_AUTOMATE_WEBHOOK_URL` | URL do Flow para alertas | ❌ |
| `ENABLE_MANUAL_TRIGGER` | Habilita trigger manual via dashboard (`true`/`false`) | ❌ |

---

## Stack

- **Backend:** Python 3.11+, Flask 3.0, Gunicorn
- **Scraping:** crawl4ai, Playwright (Chromium headless)
- **OCR/PDF:** docling (PyTorch)
- **Frontend:** HTML5, CSS3, JavaScript, Phosphor Icons
- **Infra:** Docker, Kestra (orquestrador), Nginx

---

## Roadmap

- [ ] `docker-compose.yml` para ambiente local completo
- [ ] GitHub Actions CI/CD (build + push imagem)
- [ ] Health check endpoint (`GET /health`)
- [ ] Logging estruturado (JSON para Loki/ELK)
- [ ] Autenticação no Dashboard (Flask-Login)

---

## Licença

MIT © [Lucas Santos](https://github.com/lucassantoss4)
