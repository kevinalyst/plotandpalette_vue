# Main Backend Service Dockerfile
# Plot & Palette - Flask Backend with Recommendations
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements-prod.txt .
RUN pip install --no-cache-dir -r requirements-prod.txt

# Copy backend files
COPY server.py .
COPY database.py .
COPY gunicorn.conf.py .

# Copy only required service directories (avoid sending entire build context)
COPY emotions_generation/ ./emotions_generation/
COPY painting_recommendation/ ./painting_recommendation/
# Story generation runs in a separate sidecar; not copied into backend image
# Static assets (SPA, images, gifs) are served by Nginx; not copied here

# Create uploads, logs, and runtime directories
RUN mkdir -p uploads /var/log/plot-palette /var/run/plot-palette

# Set environment variables
ENV FLASK_APP=server.py
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# Expose port (Cloud Run sidecar will access via localhost)
EXPOSE 5000

# Health check
# Healthcheck (note: Cloud Run uses its own health checks)
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Run the application with Gunicorn
CMD ["gunicorn", "-c", "gunicorn.conf.py", "server:app"] 