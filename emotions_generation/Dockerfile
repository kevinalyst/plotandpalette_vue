# Emotion Prediction API - Python 3.10 Container
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy model files and API code
COPY *.pkl ./
COPY emotion_prediction_api.py ./

# Create a simple startup script to handle model paths
RUN echo '#!/bin/bash\n\
# Create Step6.1 directory structure expected by the API\n\
mkdir -p Step6.1\n\
# Copy model files to expected location\n\
cp final_emotion_model.pkl Step6.1/\n\
cp final_scaler.pkl Step6.1/\n\
cp final_feature_info.pkl Step6.1/\n\
# Start the API\n\
python emotion_prediction_api.py --host 0.0.0.0 --port 8000' > /app/start.sh && \
chmod +x /app/start.sh

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start the application
CMD ["/app/start.sh"] 