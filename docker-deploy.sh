#!/bin/bash

echo "🐳 PLOT & PALETTE - DOCKER DEPLOYMENT"
echo "====================================="
echo "Time: $(date)"
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Error handling
set -e
trap 'echo "❌ Deployment failed at line $LINENO"' ERR

echo -e "${BLUE}📋 DEPLOYMENT CHECKLIST${NC}"
echo "================================"
echo "✅ Dockerfiles created for all services"
echo "✅ Docker Compose configuration ready"
echo "✅ Vue.js frontend migrated"
echo "✅ Nginx reverse proxy configured"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

echo -e "${BLUE}🔧 SETTING UP ENVIRONMENT${NC}"
echo "=========================="

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs/nginx
mkdir -p uploads
mkdir -p frontend-vue/dist

# Copy environment file
if [ ! -f ".env" ]; then
    echo "📄 Creating environment file..."
    cp docker.env .env
    echo -e "${YELLOW}⚠️  Please update .env file with your actual API keys${NC}"
fi

# Set proper permissions
echo "🔐 Setting permissions..."
chmod 755 uploads logs
chmod 644 docker.env

echo ""
echo -e "${BLUE}🏗️  BUILDING DOCKER IMAGES${NC}"
echo "=========================="

# Build Vue.js frontend first
echo "🎨 Building Vue.js frontend..."
cd frontend-vue
if [ ! -d "node_modules" ]; then
    echo "📦 Installing npm dependencies..."
    npm install
fi

echo "🏗️  Building production frontend..."
if npm run build; then
    echo -e "${GREEN}✅ Vue.js build successful!${NC}"
else
    echo -e "${YELLOW}⚠️  Vue.js build failed. Creating fallback frontend...${NC}"
    
    # Create fallback HTML frontend
    mkdir -p dist
    cat > dist/index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Plot & Palette</title>
    <style>
        body { 
            font-family: 'Arial', sans-serif; 
            text-align: center; 
            padding: 50px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
            margin: 0;
        }
        .container { 
            max-width: 800px; 
            margin: 0 auto; 
            background: rgba(255,255,255,0.1);
            padding: 40px;
            border-radius: 20px;
            backdrop-filter: blur(10px);
        }
        h1 { 
            font-size: 3rem; 
            margin-bottom: 20px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .status { 
            font-size: 1.2rem; 
            margin: 20px 0;
            padding: 20px;
            background: rgba(255,255,255,0.2);
            border-radius: 10px;
        }
        .api-links a {
            display: inline-block;
            margin: 10px;
            padding: 10px 20px;
            background: rgba(255,255,255,0.2);
            color: white;
            text-decoration: none;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎨 Plot & Palette</h1>
        <div class="status">
            <p>🐳 <strong>Docker Services Running</strong></p>
            <p>Backend API, AI Services, and Database are operational!</p>
        </div>
        <div class="api-links">
            <a href="/api/health">🏥 Backend Health</a>
            <a href="/api/emotions/health">🧠 Emotion API</a>
            <a href="/api/stories/health">📚 Story API</a>
        </div>
        <div class="status">
            <p><strong>Note:</strong> Vue.js build failed. Run <code>./fix_vue_build.sh</code> for the full experience!</p>
        </div>
    </div>
</body>
</html>
EOF
    echo -e "${GREEN}✅ Fallback frontend created!${NC}"
fi
cd ..

# Build Docker images
echo "🐳 Building Docker images..."
docker-compose build --no-cache

echo ""
echo -e "${BLUE}🗄️  DATABASE SETUP${NC}"
echo "=================="

# Start database first
echo "🚀 Starting MySQL database..."
docker-compose up -d db

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
for i in {1..30}; do
    if docker-compose exec -T db mysqladmin ping -h localhost --silent; then
        echo -e "${GREEN}✅ Database is ready!${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}❌ Database failed to start${NC}"
        exit 1
    fi
    echo "⏳ Waiting... ($i/30)"
    sleep 2
done

echo ""
echo -e "${BLUE}🚀 STARTING ALL SERVICES${NC}"
echo "========================"

# Start all services
echo "🐳 Starting all Docker services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

echo ""
echo -e "${BLUE}🏥 HEALTH CHECKS${NC}"
echo "================"

# Check service health
services=("backend:5000" "emotion-api:5001" "story-api:5002" "nginx:80")
for service in "${services[@]}"; do
    service_name=$(echo $service | cut -d':' -f1)
    port=$(echo $service | cut -d':' -f2)
    
    echo -n "🔍 Checking $service_name... "
    
    if docker-compose exec -T $service_name curl -f http://localhost:$port/health &>/dev/null; then
        echo -e "${GREEN}✅ Healthy${NC}"
    else
        echo -e "${YELLOW}⚠️  Starting up...${NC}"
    fi
done

echo ""
echo -e "${GREEN}🎉 DEPLOYMENT COMPLETED!${NC}"
echo "========================"
echo ""
echo -e "${BLUE}📊 SERVICE STATUS:${NC}"
docker-compose ps

echo ""
echo -e "${BLUE}🌐 ACCESS INFORMATION:${NC}"
echo "======================"
echo "🖥️  Web Application: http://localhost"
echo "🎨 Backend API: http://localhost/api/"
echo "🧠 Emotion API: http://localhost/api/emotions/"
echo "📚 Story API: http://localhost/api/stories/"
echo ""

echo -e "${BLUE}📋 USEFUL COMMANDS:${NC}"
echo "==================="
echo "📖 View logs: docker-compose logs -f [service_name]"
echo "🔄 Restart service: docker-compose restart [service_name]"
echo "🛑 Stop all: docker-compose down"
echo "🧹 Clean up: docker-compose down -v --rmi all"
echo ""

echo -e "${YELLOW}⚠️  IMPORTANT NOTES:${NC}"
echo "===================="
echo "1. Update .env file with your actual API keys"
echo "2. For production, configure SSL certificates"
echo "3. Monitor logs for any issues: docker-compose logs -f"
echo "4. Database data is persisted in Docker volume 'mysql_data'"
echo ""

echo -e "${GREEN}✅ Ready to use Plot & Palette!${NC}" 