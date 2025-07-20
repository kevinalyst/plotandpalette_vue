# Emotion Prediction API Microservice
# Plot & Palette - 15-Emotion Classification Service
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
COPY emotion_prediction_api.py .
COPY final_emotion_model.pkl .
COPY final_scaler.pkl .
COPY final_feature_info.pkl .
COPY interpretable_color_features_cleaned.csv .
COPY resampled_emotions_data.csv .

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 5001

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5001/health || exit 1

# Run the FastAPI application with Uvicorn
CMD ["uvicorn", "emotion_prediction_api:app", "--host", "0.0.0.0", "--port", "5001"] 