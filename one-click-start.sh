#!/bin/bash

# One-Click Plot & Palette Server Launcher
# ========================================
# This script intelligently detects your environment and chooses the best launch approach
# Updated to include Vue.js frontend alongside the main server

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Global variables
NODE_PATH=""
NPM_PATH=""
PYTHON_PATH=""
USE_DOCKER=false
EMOTION_API_PID=""
SERVER_PID=""
VUE_PROJECT_PID=""

echo -e "${BLUE}🎨 === Plot & Palette One-Click Launcher === 🎨${NC}"
echo "Intelligently detecting your environment and launching all services..."
echo ""

# Function to print colored output
print_status() {
    echo -e "${CYAN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_header() {
    echo -e "${BLUE}=== $1 ===${NC}"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to find Node.js installation
find_nodejs() {
    print_status "Searching for Node.js installation..."
    
    # Check common Node.js locations
    NODE_LOCATIONS=(
        "node"
        "/usr/local/bin/node"
        "/usr/bin/node"
        "/opt/homebrew/bin/node"
        "$HOME/.nvm/versions/node/*/bin/node"
        "$HOME/.n/bin/node"
        "/usr/local/node/bin/node"
        "/opt/node/bin/node"
    )
    
    # Check if nvm is available and try to activate it
    if [ -d "$HOME/.nvm" ]; then
        export NVM_DIR="$HOME/.nvm"
        [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
        [ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"
        
        if command_exists nvm; then
            print_status "NVM found, activating default Node.js version..."
            nvm use default >/dev/null 2>&1 || nvm use node >/dev/null 2>&1
        fi
    fi
    
    # Check PATH first
    if command_exists node; then
        NODE_PATH=$(which node)
        NPM_PATH=$(which npm)
        print_success "Found Node.js in PATH: $NODE_PATH"
        echo "Node.js version: $(node --version)"
        if [ -n "$NPM_PATH" ]; then
            echo "NPM version: $(npm --version)"
        fi
        return 0
    fi
    
    # Check specific paths with glob expansion
    for pattern in "${NODE_LOCATIONS[@]}"; do
        for path in $pattern; do
            if [ -f "$path" ] && [ -x "$path" ]; then
                NODE_PATH="$path"
                # Find corresponding npm
                NPM_PATH="$(dirname "$path")/npm"
                if [ ! -f "$NPM_PATH" ]; then
                    NPM_PATH=""
                fi
                print_success "Found Node.js at: $NODE_PATH"
                echo "Node.js version: $($NODE_PATH --version)"
                return 0
            fi
        done
    done
    
    print_error "Node.js not found"
    return 1
}

# Function to find Python installation
find_python() {
    print_status "Searching for Python installation..."
    
    PYTHON_LOCATIONS=(
        "python3"
        "python"
        "/usr/local/bin/python3"
        "/usr/bin/python3"
        "/opt/homebrew/bin/python3"
        "$HOME/.pyenv/shims/python3"
        "/usr/local/python/bin/python3"
    )
    
    for cmd in "${PYTHON_LOCATIONS[@]}"; do
        if command_exists "$cmd"; then
            # Check if it's Python 3
            if $cmd --version 2>&1 | grep -q "Python 3"; then
                PYTHON_PATH="$cmd"
                print_success "Found Python 3: $PYTHON_PATH"
                echo "Python version: $($PYTHON_PATH --version)"
                return 0
            fi
        fi
    done
    
    print_error "Python 3 not found"
    return 1
}

# Function to check Docker availability
check_docker() {
    print_status "Checking Docker availability..."
    
    if ! command_exists docker; then
        print_warning "Docker not installed"
        return 1
    fi
    
    if ! docker info >/dev/null 2>&1; then
        print_warning "Docker not running, attempting to start..."
        
        # Try to start Docker Desktop
        if [ -d "/Applications/Docker.app" ]; then
            open -a Docker
            print_status "Waiting for Docker to start..."
            
            # Wait up to 60 seconds for Docker to start
            for i in {1..12}; do
                sleep 5
                if docker info >/dev/null 2>&1; then
                    print_success "Docker is now running!"
                    return 0
                fi
                echo "   Still waiting... ($((i*5)) seconds)"
            done
            
            print_warning "Docker failed to start within 60 seconds"
            return 1
        else
            print_warning "Docker Desktop not found in Applications"
            return 1
        fi
    fi
    
    print_success "Docker is running"
    return 0
}

# Function to check project dependencies
check_project_dependencies() {
    print_status "Checking main project dependencies..."
    
    if [ ! -f "package.json" ]; then
        print_error "package.json not found in current directory"
        return 1
    fi
    
    if [ ! -d "node_modules" ]; then
        print_warning "node_modules not found, installing dependencies..."
        if [ -n "$NPM_PATH" ]; then
            $NPM_PATH install
        elif [ -n "$NODE_PATH" ]; then
            $(dirname "$NODE_PATH")/npm install 2>/dev/null || npm install
        else
            npm install
        fi
        
        if [ ! -d "node_modules" ]; then
            print_error "Failed to install dependencies"
            return 1
        fi
    fi
    
    print_success "Main project dependencies are ready"
    return 0
}

# Function to check Vue project dependencies
check_vue_project_dependencies() {
    print_status "Checking Vue project dependencies..."
    
    if [ ! -d "vue-project" ]; then
        print_error "vue-project directory not found"
        return 1
    fi
    
    if [ ! -f "vue-project/package.json" ]; then
        print_error "vue-project/package.json not found"
        return 1
    fi
    
    if [ ! -d "vue-project/node_modules" ]; then
        print_warning "Vue project node_modules not found, installing dependencies..."
        cd vue-project
        
        # Clean any existing problematic installations
        if [ -d "node_modules" ]; then
            rm -rf node_modules
        fi
        if [ -f "package-lock.json" ]; then
            rm -f package-lock.json
        fi
        
        # Install with legacy peer deps to handle conflicts
        if [ -n "$NPM_PATH" ]; then
            $NPM_PATH install --legacy-peer-deps
        elif [ -n "$NODE_PATH" ]; then
            $(dirname "$NODE_PATH")/npm install --legacy-peer-deps 2>/dev/null || npm install --legacy-peer-deps
        else
            npm install --legacy-peer-deps
        fi
        cd ..
        
        if [ ! -d "vue-project/node_modules" ]; then
            print_error "Failed to install Vue project dependencies"
            return 1
        fi
    fi
    
    print_success "Vue project dependencies are ready"
    return 0
}

# Function to check Python dependencies
check_python_dependencies() {
    print_status "Checking Python dependencies..."
    
    if [ -z "$PYTHON_PATH" ]; then
        print_error "Python not available"
        return 1
    fi
    
    # Check required packages
    REQUIRED_PACKAGES=("flask" "joblib" "pandas" "numpy" "scikit-learn")
    MISSING_PACKAGES=()
    
    for package in "${REQUIRED_PACKAGES[@]}"; do
        if ! $PYTHON_PATH -c "import $package" 2>/dev/null; then
            MISSING_PACKAGES+=("$package")
        fi
    done
    
    if [ ${#MISSING_PACKAGES[@]} -gt 0 ]; then
        print_warning "Missing Python packages: ${MISSING_PACKAGES[*]}"
        print_status "Installing missing packages..."
        
        for package in "${MISSING_PACKAGES[@]}"; do
            $PYTHON_PATH -m pip install "$package" --user
        done
    fi
    
    print_success "Python dependencies are ready"
    return 0
}

# Function to check if port is available
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 1
    fi
    return 0
}

# Function to kill process on port
kill_port_process() {
    local port=$1
    print_warning "Freeing port $port..."
    lsof -ti:$port | xargs kill -9 2>/dev/null
    sleep 2
}

# Function to start containerized services
start_containerized_services() {
    print_header "Starting Containerized Services"
    
    # Check if docker-compose is available
    if ! command_exists docker-compose; then
        print_error "docker-compose not available"
        return 1
    fi
    
    # Build and start containers
    print_status "Building containers..."
    if ! docker-compose build; then
        print_error "Failed to build containers"
        return 1
    fi
    
    print_status "Starting services..."
    if ! docker-compose up -d; then
        print_error "Failed to start services"
        return 1
    fi
    
    # Wait for services to be ready
    print_status "Waiting for services to be ready..."
    sleep 10
    
    # Check if emotion API is healthy
    print_status "Checking emotion API health..."
    for i in {1..6}; do
        if curl -f http://localhost:8000/health >/dev/null 2>&1; then
            print_success "Emotion API is healthy"
            export USE_CONTAINERS=true
            return 0
        fi
        sleep 5
        echo "   Waiting for API... (attempt $i/6)"
    done
    
    print_error "Emotion API not responding"
    docker-compose logs emotion-api
    return 1
}

# Function to start emotion prediction API (traditional)
start_emotion_api() {
    print_status "Starting emotion prediction API..."
    
    if [ ! -f "emotions_generation/emotion_prediction_api.py" ]; then
        print_error "emotion_prediction_api.py not found"
        return 1
    fi
    
    # Check if API is already running
    if ! check_port 5001; then
        print_warning "Port 5001 in use, attempting to free it..."
        kill_port_process 5001
    fi
    
    # Start the API in background
    cd emotions_generation
    $PYTHON_PATH emotion_prediction_api.py > ../emotion_api.log 2>&1 &
    EMOTION_API_PID=$!
    cd ..
    
    # Wait for API to start
    sleep 3
    
    # Check if API started successfully
    for i in {1..5}; do
        if curl -s http://localhost:5001/health >/dev/null 2>&1; then
            print_success "Emotion prediction API started (PID: $EMOTION_API_PID)"
            return 0
        fi
        sleep 2
    done
    
    print_error "Failed to start emotion prediction API"
    return 1
}

# Function to start main server
start_main_server() {
    print_status "Starting main server..."
    
    if [ ! -f "server.js" ]; then
        print_error "server.js not found"
        return 1
    fi
    
    # Check if port 3000 is available
    if ! check_port 3000; then
        print_warning "Port 3000 in use, attempting to free it..."
        kill_port_process 3000
    fi
    
    # Start the server
    if [ -n "$NODE_PATH" ]; then
        $NODE_PATH server.js > server.log 2>&1 &
    else
        node server.js > server.log 2>&1 &
    fi
    
    SERVER_PID=$!
    
    # Wait for server to start
    sleep 3
    
    # Check if server is running
    for i in {1..5}; do
        if curl -s http://localhost:3000 >/dev/null 2>&1; then
            print_success "Main server started (PID: $SERVER_PID)"
            return 0
        fi
        sleep 2
    done
    
    print_error "Failed to start main server"
    return 1
}

# Function to start Vue project
start_vue_project() {
    print_status "Starting Vue project..."
    
    if [ ! -d "vue-project" ]; then
        print_error "vue-project directory not found"
        return 1
    fi
    
    # Check if port 8080 is available
    if ! check_port 8080; then
        print_warning "Port 8080 in use, attempting to free it..."
        kill_port_process 8080
    fi
    
    # Start the Vue development server with proper NVM environment
    cd vue-project
    
    # Set up NVM environment for the Vue project
    export NVM_DIR="$HOME/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
    
    if [ -n "$NPM_PATH" ]; then
        # Use the full path and set up NODE_PATH
        NODE_DIR=$(dirname "$NODE_PATH")
        export PATH="$NODE_DIR:$PATH"
        $NPM_PATH run dev > ../vue-project.log 2>&1 &
    elif [ -n "$NODE_PATH" ]; then
        # Use the full path and set up NODE_PATH
        NODE_DIR=$(dirname "$NODE_PATH")
        export PATH="$NODE_DIR:$PATH"
        $NODE_DIR/npm run dev > ../vue-project.log 2>&1 &
    else
        # Fallback to system npm
        npm run dev > ../vue-project.log 2>&1 &
    fi
    
    VUE_PROJECT_PID=$!
    cd ..
    
    # Wait for Vue project to start
    sleep 5
    
    # Check if Vue project is running
    for i in {1..10}; do
        if curl -s http://localhost:8080 >/dev/null 2>&1; then
            print_success "Vue project started (PID: $VUE_PROJECT_PID)"
            return 0
        fi
        sleep 2
        echo "   Waiting for Vue project... (attempt $i/10)"
    done
    
    print_error "Failed to start Vue project"
    print_warning "Check vue-project.log for details"
    return 1
}

# Function to display final status
show_final_status() {
    echo ""
    print_header "🎉 Launch Complete!"
    
    if [ "$USE_DOCKER" = true ]; then
        echo "🐳 Running in containerized mode"
        echo ""
        echo "📊 Services:"
        echo "  🎨 Vue Frontend: http://localhost:8080"
        echo "  🌐 Main Server: http://localhost:3000"
        echo "  🧠 Emotion API: http://localhost:8000"
        echo "  📖 API Documentation: http://localhost:8000/docs"
        echo "  ❤️  Health Check: http://localhost:8000/health"
        echo ""
        echo "🚀 Primary Interface: http://localhost:8080 (Vue.js App)"
        echo ""
        echo "🛑 To stop services:"
        echo "  docker-compose down"
        echo "  Press Ctrl+C to stop all servers"
    else
        echo "🖥️  Running in traditional mode"
        echo ""
        echo "📊 Services:"
        echo "  🎨 Vue Frontend: http://localhost:8080"
        echo "  🌐 Main Server: http://localhost:3000"
        echo "  🧠 Emotion API: http://localhost:5001"
        echo ""
        echo "🚀 Primary Interface: http://localhost:8080 (Vue.js App)"
        echo ""
        echo "🛑 To stop services:"
        echo "  Press Ctrl+C to stop all servers"
    fi
    
    echo ""
    echo "📋 Logs:"
    if [ "$USE_DOCKER" = true ]; then
        echo "  docker-compose logs -f"
    else
        echo "  Main server: cat server.log"
        echo "  Emotion API: cat emotion_api.log"
        echo "  Vue project: cat vue-project.log"
    fi
    
    echo ""
    echo "💡 Pro Tip: Use the Vue.js interface at http://localhost:8080 for the best experience!"
}

# Function to cleanup on exit
cleanup() {
    echo ""
    print_warning "Shutting down services..."
    
    if [ "$USE_DOCKER" = true ]; then
        docker-compose down
    else
        if [ -n "$EMOTION_API_PID" ]; then
            kill $EMOTION_API_PID 2>/dev/null
            print_status "Stopped emotion API (PID: $EMOTION_API_PID)"
        fi
        if [ -n "$SERVER_PID" ]; then
            kill $SERVER_PID 2>/dev/null
            print_status "Stopped main server (PID: $SERVER_PID)"
        fi
        if [ -n "$VUE_PROJECT_PID" ]; then
            kill $VUE_PROJECT_PID 2>/dev/null
            print_status "Stopped Vue project (PID: $VUE_PROJECT_PID)"
        fi
    fi
    
    # Clean up any remaining processes on our ports
    kill_port_process 3000
    kill_port_process 5001
    kill_port_process 8000
    kill_port_process 8080
    
    print_success "Cleanup complete"
    exit 0
}

# Main execution function
main() {
    print_status "Current directory: $(pwd)"
    echo ""
    
    # Step 1: Environment Detection
    print_header "🔍 Environment Detection"
    
    # Check Docker first (preferred approach)
    if check_docker; then
        USE_DOCKER=true
        print_success "Docker available - will use containerized approach"
    else
        print_warning "Docker not available - will use traditional approach"
        
        # For traditional approach, we need Node.js and Python
        if ! find_nodejs; then
            print_error "Node.js is required but not found"
            print_error "Please install Node.js and try again"
            exit 1
        fi
        
        if ! find_python; then
            print_error "Python 3 is required but not found"
            print_error "Please install Python 3 and try again"
            exit 1
        fi
    fi
    
    echo ""
    
    # Step 2: Dependency Check
    print_header "📦 Dependency Check"
    
    if [ "$USE_DOCKER" = true ]; then
        # For Docker, we still need Node.js for the main server and Vue project
        if ! find_nodejs; then
            print_error "Node.js is required for the main server and Vue project"
            exit 1
        fi
        
        if ! check_project_dependencies; then
            exit 1
        fi
        
        if ! check_vue_project_dependencies; then
            exit 1
        fi
    else
        # For traditional approach, check all dependencies
        if ! check_project_dependencies; then
            exit 1
        fi
        
        if ! check_vue_project_dependencies; then
            exit 1
        fi
        
        if ! check_python_dependencies; then
            print_warning "Python dependencies check failed, but continuing..."
        fi
    fi
    
    echo ""
    
    # Step 3: Service Launch
    print_header "🚀 Service Launch"
    
    if [ "$USE_DOCKER" = true ]; then
        if ! start_containerized_services; then
            print_error "Failed to start containerized services"
            exit 1
        fi
    else
        if ! start_emotion_api; then
            print_warning "Failed to start emotion API, but continuing..."
        fi
    fi
    
    if ! start_main_server; then
        print_error "Failed to start main server"
        exit 1
    fi
    
    if ! start_vue_project; then
        print_error "Failed to start Vue project"
        exit 1
    fi
    
    # Step 4: Show final status
    show_final_status
    
    # Wait for user interruption
    print_status "Press Ctrl+C to stop all services"
    wait
}

# Handle script interruption
trap cleanup INT TERM

# Run main function
main "$@" 