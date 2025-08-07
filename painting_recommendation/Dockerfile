# Painting Recommendation Service
# Plot & Palette - Cluster-based Painting Recommendation Service
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
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY recommendation_service.py .
COPY cluster_color_palettes.csv .
COPY colour_data_with_clusters_3.0.csv .

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 5003

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5003/health || exit 1

# Run the recommendation service
CMD ["python3", "recommendation_service.py"]