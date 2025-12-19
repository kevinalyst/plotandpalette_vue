#!/bin/bash

# Plot & Palette - Quick Setup Script
# This script automates the initial setup for new collaborators

set -e  # Exit on any error

echo "🎨 Plot & Palette - Quick Setup Script"
echo "======================================="
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on macOS or Linux
OS="unknown"
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
fi

print_status "Detected OS: $OS"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
print_status "Checking prerequisites..."

# Check Docker
if command_exists docker; then
    print_success "Docker is installed"
    if docker --version | grep -q "Docker version"; then
        docker --version
    fi
else
    print_error "Docker is not installed. Please install Docker Desktop from https://www.docker.com/products/docker-desktop"
    exit 1
fi

# Check Docker Compose
if command_exists docker-compose || docker compose version >/dev/null 2>&1; then
    print_success "Docker Compose is available"
else
    print_error "Docker Compose is not available. Please ensure Docker Desktop is properly installed."
    exit 1
fi

# Check Node.js (optional for frontend development)
if command_exists node; then
    print_success "Node.js is installed: $(node --version)"
    if command_exists npm; then
        print_success "npm is installed: $(npm --version)"
    fi
else
    print_warning "Node.js is not installed. This is optional but recommended for frontend development."
    print_warning "You can install it from https://nodejs.org/"
fi

# Check Git
if command_exists git; then
    print_success "Git is installed: $(git --version)"
else
    print_error "Git is not installed. Please install Git from https://git-scm.com/downloads"
    exit 1
fi

echo ""
print_status "All prerequisites check passed!"
echo ""

# Setup environment file
print_status "Setting up environment configuration..."

if [ ! -f "docker.env" ]; then
    if [ -f "docker.env.example" ]; then
        cp docker.env.example docker.env
        print_success "Created docker.env from template"
        print_warning "You may want to customize docker.env for your environment"
    else
        print_error "docker.env.example not found. Creating minimal docker.env..."
        cat > docker.env << EOF
# Database Configuration - Google Cloud SQL (UPDATE THESE VALUES!)
DB_HOST=your_database_host_here
DB_PORT=3306
DB_NAME=your_database_name_here
DB_USER=your_database_user_here
DB_PASSWORD=your_database_password_here

# MySQL Root Configuration (Legacy - keeping for reference)
MYSQL_ROOT_PASSWORD=plot_palette_root_2024
MYSQL_DATABASE=plot_palette
MYSQL_USER=app_user
MYSQL_PASSWORD=secure_app_password_2024

# Flask Configuration
FLASK_ENV=production
FLASK_APP=server.py
DEBUG=False

# Claude AI Configuration (SET YOUR ACTUAL API KEY!)
OPENAI_API_KEY=your_openai_api_key_here

# Application Configuration
PYTHONUNBUFFERED=1
PYTHONPATH=/app
LOG_LEVEL=INFO
EOF
        print_success "Created basic docker.env file"
        print_warning "⚠️  IMPORTANT: You MUST update docker.env with your actual database credentials and API keys!"
        print_warning "   - Set DB_HOST, DB_NAME, DB_USER, DB_PASSWORD for your Google Cloud SQL instance"
        print_warning "   - Set OPENAI_API_KEY for OpenAI story generation"
    fi
else
    print_success "docker.env already exists"
fi

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p logs/application logs/nginx uploads
print_success "Created log and upload directories"

# Stop any existing containers
print_status "Stopping any existing Plot & Palette containers..."
docker-compose down --remove-orphans 2>/dev/null || true

# Build and start services
print_status "Building and starting all services..."
print_warning "This may take several minutes on first run..."

if docker-compose up --build -d; then
    print_success "All services started successfully!"
else
    print_error "Failed to start services. Check the logs with: docker-compose logs"
    exit 1
fi

# Wait for services to be ready
print_status "Waiting for services to initialize..."
sleep 30

# Initialize database (skip for Google Cloud SQL)
print_status "Checking database connection..."
if docker-compose exec -T backend python -c "from database import db; print('Database connection:', 'OK' if db.health_check() else 'Failed')"; then
    print_success "Database connection verified!"
else
    print_warning "Database connection failed. Check your Google Cloud SQL configuration in docker.env"
    print_warning "Make sure your database credentials and network access are correct"
fi

# Setup frontend (if Node.js is available)
if command_exists node && command_exists npm; then
    print_status "Setting up frontend..."
    cd frontend-vue
    
    if [ ! -d "node_modules" ]; then
        print_status "Installing frontend dependencies..."
        npm install
        print_success "Frontend dependencies installed"
    else
        print_success "Frontend dependencies already installed"
    fi
    
    print_status "Building frontend for production..."
    if npm run build; then
        print_success "Frontend built successfully!"
    else
        print_warning "Frontend build failed. You can try building manually later with:"
        print_warning "cd frontend-vue && npm install && npm run build"
    fi
    
    cd ..
else
    print_warning "Skipping frontend setup (Node.js not available)"
    print_warning "You can set up the frontend later with:"
    print_warning "cd frontend-vue && npm install && npm run build"
fi

# Check service health
print_status "Checking service health..."
sleep 10

# Function to check service health
check_service() {
    local service_name=$1
    local url=$2
    local max_attempts=5
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" >/dev/null 2>&1; then
            print_success "$service_name is healthy"
            return 0
        fi
        print_status "Attempt $attempt/$max_attempts: Waiting for $service_name..."
        sleep 5
        ((attempt++))
    done
    
    print_warning "$service_name may not be ready yet"
    return 1
}

# Check each service
check_service "Main Application" "http://localhost"
check_service "Backend API" "http://localhost:5003/health"
check_service "Story API" "http://localhost:5002/health"
# Note: Emotion and Recommendation services are embedded in the backend

echo ""
print_success "🎉 Setup completed!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
print_status "Your Plot & Palette application is ready!"
echo ""
echo "🌐 Access the application: ${GREEN}http://localhost${NC}"
echo ""
echo "📋 Useful commands:"
echo "   View logs:           docker-compose logs"
echo "   Stop services:       docker-compose down"
echo "   Restart services:    docker-compose restart"
echo "   Check status:        docker-compose ps"
echo ""
if command_exists node; then
    echo "🔧 Frontend development:"
    echo "   Start dev server:    cd frontend-vue && npm run serve"
    echo "   Build production:    cd frontend-vue && npm run build"
    echo ""
fi
echo "🏥 Health monitoring:"
echo "   Run diagnostics:     python diagnostic.py"
echo "   Backend health:      curl http://localhost/api/health"
echo ""
echo "📖 Read the full README.md for detailed documentation"
echo ""
print_success "Happy coding! 🎨✨" 