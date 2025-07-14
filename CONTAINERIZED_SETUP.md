# Containerized Palette Analysis Setup

This document explains how to use the containerized setup to resolve Python version conflicts between the emotion prediction API (requires Python 3.10) and the recommendation service (uses Python 3.13).

## 🎯 Problem Solved

The emotion prediction model was trained in Python 3.10, but the main application uses Python 3.13. This creates compatibility issues. The containerized solution isolates each service in its own environment.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Main Application                         │
│                   (Node.js Server)                         │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                Docker Compose                               │
│                                                             │
│  ┌─────────────────────┐    ┌─────────────────────────────┐ │
│  │   Emotion API       │    │  Recommendation Service     │ │
│  │   (Python 3.10)     │    │     (Python 3.13)          │ │
│  │                     │    │                             │ │
│  │ - FastAPI Server    │    │ - Color Extraction         │ │
│  │ - ML Model          │    │ - Palette Analysis         │ │
│  │ - Port 8000         │    │ - Calls Emotion API        │ │
│  └─────────────────────┘    └─────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 📋 Prerequisites

1. **Docker**: Install Docker Desktop
2. **Docker Compose**: Usually included with Docker Desktop
3. **Node.js**: For the main application server

## 🚀 Quick Start

### 1. Start the Containerized Services

```bash
# Make the startup script executable (if not already done)
chmod +x start-containers.sh

# Start all services
./start-containers.sh
```

This will:
- Build both Docker containers
- Start the emotion API (Python 3.10) on port 8000
- Start the recommendation service (Python 3.13)
- Verify all services are healthy

### 2. Start the Main Application

```bash
# Set environment variable to use containers
export USE_CONTAINERS=true

# Start the Node.js server
npm start
```

Or in one command:
```bash
USE_CONTAINERS=true npm start
```

## 🔧 Manual Container Management

### Build Containers
```bash
docker-compose build
```

### Start Services
```bash
docker-compose up -d
```

### Stop Services
```bash
docker-compose down
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f emotion-api
docker-compose logs -f recommendation-service
```

### Restart a Service
```bash
docker-compose restart emotion-api
```

## 🧪 Testing the Setup

### 1. Test Emotion API Directly
```bash
# Health check
curl http://localhost:8000/health

# Test prediction
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "colors": {
      "red": 0.3,
      "blue": 0.2,
      "green": 0.1,
      "yellow": 0.15,
      "purple": 0.1,
      "orange": 0.05,
      "pink": 0.05,
      "turquoise": 0.02,
      "brown": 0.02,
      "grey": 0.01,
      "black": 0.0,
      "white": 0.0
    }
  }'
```

### 2. Test Full Pipeline
Upload an image through the web interface and check that:
- Colors are extracted correctly
- Emotion prediction works
- Recommendations are generated

## 📁 File Structure

```
plot&palette/
├── docker-compose.yml              # Orchestrates both services
├── start-containers.sh             # Startup script
├── Dockerfile.recommendation       # Recommendation service container
├── emotions_generation2.0/
│   ├── Dockerfile                  # Emotion API container
│   ├── emotion_prediction_api.py   # FastAPI server
│   ├── requirements.txt            # Python 3.10 dependencies
│   └── *.pkl                       # ML model files
├── Recommandations/
│   └── containerized_recommandations.py  # Modified recommendation script
└── server.js                       # Updated to support containers
```

## 🔄 How It Works

1. **Image Upload**: User uploads an image via the web interface
2. **Color Extraction**: Recommendation service extracts colors from the image
3. **Feature Engineering**: Creates 85 color features from the extracted colors
4. **Emotion Prediction**: Calls the emotion API with the 12 basic color features
5. **Recommendation Generation**: Uses all 85 features to find similar paintings
6. **Response**: Returns recommendations with emotion prediction

## 🐛 Troubleshooting

### Services Won't Start
```bash
# Check Docker is running
docker info

# Check for port conflicts
lsof -i :8000

# View detailed logs
docker-compose logs
```

### API Not Responding
```bash
# Check service health
curl http://localhost:8000/health

# Restart the emotion API
docker-compose restart emotion-api
```

### Container Build Fails
```bash
# Clean build (removes cache)
docker-compose build --no-cache

# Check for space issues
docker system df
docker system prune
```

### Python Version Issues
The containers handle Python versions automatically. If you see version conflicts, make sure you're using the containerized setup:
```bash
export USE_CONTAINERS=true
```

## 📊 API Documentation

When the emotion API is running, you can access:
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Model Info**: http://localhost:8000/model-info

## 🔒 Security Notes

- Containers run in isolated environments
- No direct file system access between containers
- Network communication only through defined ports
- Models and data are contained within their respective containers

## 🎯 Benefits

1. **Isolation**: Each service runs in its own Python environment
2. **Consistency**: Same environment across different machines
3. **Scalability**: Easy to scale individual services
4. **Maintainability**: Clear separation of concerns
5. **Deployment**: Ready for production deployment

## 📝 Environment Variables

- `USE_CONTAINERS=true`: Enables containerized mode in server.js
- `PYTHONUNBUFFERED=1`: Ensures Python output is not buffered

## 🔄 Switching Between Modes

### Use Containers (Recommended)
```bash
export USE_CONTAINERS=true
npm start
```

### Use Local Python (Legacy)
```bash
export USE_CONTAINERS=false
# or simply
npm start
```

## 🚀 Production Deployment

For production, consider:
1. Using a container orchestration platform (Kubernetes, Docker Swarm)
2. Setting up proper monitoring and logging
3. Using environment-specific configurations
4. Implementing load balancing for high availability

This containerized setup provides a robust, scalable solution for handling the Python version conflicts while maintaining the full functionality of your palette analysis application. 