"""
run_web.py — DevRadar Web Server Entry Point

Sobe o servidor Flask para servir o Dashboard.
Para produção, use Gunicorn:

    gunicorn --bind 0.0.0.0:5000 --workers 2 run_web:app

Zero lógica de scraping aqui. O worker é responsabilidade do worker.py.
"""
import logging
from app import create_app

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

app = create_app()

if __name__ == "__main__":
    # Desenvolvimento local apenas
    app.run(debug=True, port=5000, use_reloader=True)
