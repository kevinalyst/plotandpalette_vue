# Gunicorn configuration for Plot & Palette Python backend
import multiprocessing
import os

# Server socket
bind = "0.0.0.0:5000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 300  # 5 minutes for ML processing
keepalive = 2

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000
max_requests_jitter = 100

# Logging
loglevel = "info"
accesslog = "/var/log/plot-palette/access.log"
errorlog = "/var/log/plot-palette/error.log"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "plot-palette-backend"

# Server mechanics
daemon = False
pidfile = "/var/run/plot-palette/gunicorn.pid"
user = "www-data"
group = "www-data"
tmp_upload_dir = None

# SSL (uncomment if using SSL termination at Gunicorn level)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"

# Environment
raw_env = [
    "FLASK_ENV=production",
    "PYTHONPATH=/var/www/plot-palette"
]

# Preload app for better performance
preload_app = True

# Worker configuration for ML workloads
worker_tmp_dir = "/dev/shm"  # Use tmpfs for better performance

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

def when_ready(server):
    server.log.info("Plot & Palette backend is ready to serve requests")

def worker_int(worker):
    worker.log.info("Worker received INT or QUIT signal")

def pre_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_worker_init(worker):
    worker.log.info("Worker initialized (pid: %s)", worker.pid)

def worker_abort(worker):
    worker.log.info("Worker received SIGABRT signal") 