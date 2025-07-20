# Story Generation API Microservice
# Plot & Palette - Claude AI Story Generation Service
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
COPY working_story_generator.py .
COPY API_SECURITY.md .
COPY prompt_enigineering.txt .

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

# Create a simple Flask wrapper for the story generator
RUN echo 'from flask import Flask, request, jsonify\n\
import subprocess\n\
import json\n\
import sys\n\
import os\n\
\n\
app = Flask(__name__)\n\
\n\
@app.route("/health")\n\
def health_check():\n\
    return {"status": "healthy", "service": "story-generation"}\n\
\n\
@app.route("/generate", methods=["POST"])\n\
def generate_story():\n\
    try:\n\
        data = request.get_json()\n\
        # Call the working story generator\n\
        result = subprocess.run(\n\
            [sys.executable, "working_story_generator.py", json.dumps(data)],\n\
            capture_output=True,\n\
            text=True,\n\
            timeout=30\n\
        )\n\
        \n\
        if result.returncode == 0:\n\
            return json.loads(result.stdout)\n\
        else:\n\
            return {"success": False, "error": result.stderr}, 500\n\
    except Exception as e:\n\
        return {"success": False, "error": str(e)}, 500\n\
\n\
if __name__ == "__main__":\n\
    app.run(host="0.0.0.0", port=5002)' > story_api.py

# Run the Flask API wrapper
CMD ["python", "story_api.py"] 