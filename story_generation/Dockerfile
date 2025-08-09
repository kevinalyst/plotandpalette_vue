# Story Generation API Microservice
# Plot & Palette - OpenAI Story Generation Service
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY image_story_generator.py .
COPY secure_story_generator.py .
COPY API_SECURITY.md .

# Create directories for logs and temporary files
RUN mkdir -p logs temp

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 5002

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5002/health || exit 1

# Copy the custom Flask API wrapper
COPY story_api.py .

# Run the Flask API wrapper
CMD ["python", "story_api.py"] 