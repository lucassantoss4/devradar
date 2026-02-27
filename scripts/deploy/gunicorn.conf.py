import multiprocessing

# --- GUNICORN SETTINGS ---
bind = "127.0.0.1:5000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
timeout = 120
keepalive = 2

# Logging
accesslog = "-" # Log para o stdout
errorlog = "-"  # Log para o stderr
loglevel = "info"

# Process name
proc_name = "inova-monitoring"
