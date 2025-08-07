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

# Copy static assets and service directories
COPY . ./temp_assets/
RUN mkdir -p "./15 emotion illustrations" "./palette GIF" ./image ./emotions_generation ./painting_recommendation ./story_generation && \
    cp -r "./temp_assets/15 emotion illustrations/"* "./15 emotion illustrations/" 2>/dev/null || true && \
    cp -r "./temp_assets/palette GIF/"* "./palette GIF/" 2>/dev/null || true && \
    cp -r ./temp_assets/image/* ./image/ 2>/dev/null || true && \
    cp -r "./temp_assets/emotions_generation/"* ./emotions_generation/ 2>/dev/null || true && \
    cp -r "./temp_assets/painting_recommendation/"* ./painting_recommendation/ 2>/dev/null || true && \
    cp -r "./temp_assets/story_generation/"* ./story_generation/ 2>/dev/null || true && \
    rm -rf ./temp_assets

# Create uploads, logs, and runtime directories
RUN mkdir -p uploads frontend-vue/dist/static/uploads /var/log/plot-palette /var/run/plot-palette

# Set environment variables
ENV FLASK_APP=server.py
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# Run the application with Gunicorn
CMD ["gunicorn", "-c", "gunicorn.conf.py", "server:app"] 