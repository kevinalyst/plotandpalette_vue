#!/bin/bash
# Plot & Palette - macOS Local Development Setup

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="plot-palette"
PROJECT_DIR="$(pwd)"
LOG_DIR="$PROJECT_DIR/logs"
PID_DIR="$PROJECT_DIR/pids"

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

# Check if Homebrew is installed
check_homebrew() {
    if ! command -v brew &> /dev/null; then
        print_error "Homebrew not found. Please install Homebrew first:"
        print_error "https://brew.sh"
        exit 1
    fi
}

# Install system dependencies using Homebrew
install_system_deps() {
    print_status "Installing system dependencies with Homebrew..."
    
    # Check if packages are already installed
    packages=("nginx" "mysql" "python@3.11")
    
    for package in "${packages[@]}"; do
        if brew list "$package" &> /dev/null; then
            print_status "$package is already installed"
        else
            print_status "Installing $package..."
            brew install "$package"
        fi
    done
    
    print_success "System dependencies installed"
}

# Setup MySQL database
setup_mysql() {
    print_status "Setting up MySQL database..."
    
    # Start MySQL service
    brew services start mysql
    
    print_status "Creating database and user..."
    print_warning "You may be prompted for MySQL root password"
    
    # Create database and user
    mysql -u root -p <<EOF
CREATE DATABASE IF NOT EXISTS plot_palette CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'plot_palette_user'@'localhost' IDENTIFIED BY 'dev_password_123';
GRANT ALL PRIVILEGES ON plot_palette.* TO 'plot_palette_user'@'localhost';
FLUSH PRIVILEGES;
EOF
    
    print_success "MySQL database configured"
}

# Create project directories
create_directories() {
    print_status "Creating project directories..."
    
    mkdir -p "$LOG_DIR"
    mkdir -p "$PID_DIR"
    mkdir -p "$PROJECT_DIR/uploads"
    
    chmod 755 "$PROJECT_DIR/uploads"
    chmod 755 "$LOG_DIR"
    chmod 755 "$PID_DIR"
    
    print_success "Directories created"
}

# Setup Python environment
setup_python_env() {
    print_status "Setting up Python virtual environment..."
    
    # Use Python 3.11 from Homebrew
    PYTHON_PATH="/opt/homebrew/bin/python3.11"
    
    if [ ! -f "$PYTHON_PATH" ]; then
        PYTHON_PATH="/usr/local/bin/python3.11"
    fi
    
    if [ ! -f "$PYTHON_PATH" ]; then
        PYTHON_PATH="python3"
    fi
    
    # Create virtual environment
    $PYTHON_PATH -m venv venv
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install production requirements
    if [ -f "requirements-prod.txt" ]; then
        pip install -r requirements-prod.txt
    else
        print_warning "requirements-prod.txt not found, installing basic requirements"
        pip install flask gunicorn mysql-connector-python anthropic python-dotenv
    fi
    
    deactivate
    
    print_success "Python environment configured"
}

# Configure Nginx for macOS
configure_nginx() {
    print_status "Configuring Nginx for macOS..."
    
    # Create nginx configuration for macOS
    NGINX_CONFIG="/opt/homebrew/etc/nginx/nginx.conf"
    if [ ! -f "$NGINX_CONFIG" ]; then
        NGINX_CONFIG="/usr/local/etc/nginx/nginx.conf"
    fi
    
    # Backup original config
    cp "$NGINX_CONFIG" "$NGINX_CONFIG.backup"
    
    # Create custom config
    cat > "$NGINX_CONFIG" <<EOF
events {
    worker_connections 1024;
}

http {
    include       mime.types;
    default_type  application/octet-stream;
    
    server {
        listen 8080;
        server_name localhost;
        
        # Static files
        location / {
            root $PROJECT_DIR;
            index index.html;
            try_files \$uri \$uri/ =404;
        }
        
        # API proxy
        location /api/ {
            proxy_pass http://127.0.0.1:5000;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        }
        
        # Uploads
        location /uploads/ {
            alias $PROJECT_DIR/uploads/;
        }
        
        # Static assets
        location /image/ {
            alias $PROJECT_DIR/image/;
        }
        
        location /palette\ GIF/ {
            alias $PROJECT_DIR/palette\ GIF/;
        }
        
        location /15\ emotion\ illustrations/ {
            alias $PROJECT_DIR/15\ emotion\ illustrations/;
        }
    }
}
EOF
    
    # Test nginx configuration
    nginx -t
    
    print_success "Nginx configured"
}

# Initialize database
init_database() {
    print_status "Initializing database..."
    
    source venv/bin/activate
    
    # Set environment variables
    export DB_HOST="localhost"
    export DB_USER="plot_palette_user"
    export DB_PASSWORD="dev_password_123"
    export DB_NAME="plot_palette"
    
    # Initialize database
    python3 -c "
from database import db
try:
    db.init_database()
    print('Database initialized successfully')
except Exception as e:
    print(f'Error initializing database: {e}')
    exit(1)
"
    
    deactivate
    
    print_success "Database initialized"
}

# Create environment file
create_env_file() {
    print_status "Creating environment configuration..."
    
    cat > "$PROJECT_DIR/.env" <<EOF
# Development Environment Configuration
FLASK_ENV=development
FLASK_DEBUG=True

# Database Configuration
DB_HOST=localhost
DB_USER=plot_palette_user
DB_PASSWORD=dev_password_123
DB_NAME=plot_palette
DB_PORT=3306

# Security
SECRET_KEY=$(openssl rand -hex 32)

# Logging
LOG_LEVEL=DEBUG

# Application
UPLOAD_FOLDER=$PROJECT_DIR/uploads
MAX_CONTENT_LENGTH=52428800
EOF
    
    chmod 600 "$PROJECT_DIR/.env"
    
    print_success "Environment file created"
}

# Create start/stop scripts
create_control_scripts() {
    print_status "Creating control scripts..."
    
    # Start script
    cat > "$PROJECT_DIR/start.sh" <<EOF
#!/bin/bash
cd "$PROJECT_DIR"

# Start MySQL
brew services start mysql

# Start Nginx
sudo nginx

# Start Flask app
source venv/bin/activate
export FLASK_ENV=development
gunicorn -c gunicorn.conf.py server:app --daemon

echo "Services started:"
echo "- Frontend: http://localhost:8080"
echo "- Backend: http://localhost:5000"
echo "- MySQL: localhost:3306"
EOF
    
    # Stop script
    cat > "$PROJECT_DIR/stop.sh" <<EOF
#!/bin/bash

# Stop Nginx
sudo nginx -s stop

# Stop Gunicorn
if [ -f "$PID_DIR/gunicorn.pid" ]; then
    kill \$(cat "$PID_DIR/gunicorn.pid")
    rm "$PID_DIR/gunicorn.pid"
fi

# Stop MySQL (optional)
# brew services stop mysql

echo "Services stopped"
EOF
    
    chmod +x "$PROJECT_DIR/start.sh"
    chmod +x "$PROJECT_DIR/stop.sh"
    
    print_success "Control scripts created"
}

# Main deployment function
deploy() {
    print_status "Starting Plot & Palette macOS setup..."
    
    check_homebrew
    install_system_deps
    create_directories
    setup_python_env
    create_env_file
    setup_mysql
    init_database
    configure_nginx
    create_control_scripts
    
    print_success "Setup completed successfully!"
    print_status "Your Plot & Palette application is ready"
    print_status "To start the application:"
    print_status "  ./start.sh"
    print_status "To stop the application:"
    print_status "  ./stop.sh"
    print_warning "Frontend will be available at: http://localhost:8080"
    print_warning "Backend API will be available at: http://localhost:5000"
}

# Function to start services
start_services() {
    print_status "Starting services..."
    
    # Start MySQL
    brew services start mysql
    
    # Start Nginx
    sudo nginx
    
    # Start Flask app
    source venv/bin/activate
    export FLASK_ENV=development
    gunicorn -c gunicorn.conf.py server:app --daemon
    
    print_success "Services started"
    print_status "Frontend: http://localhost:8080"
    print_status "Backend: http://localhost:5000"
}

# Function to stop services
stop_services() {
    print_status "Stopping services..."
    
    # Stop Nginx
    sudo nginx -s stop 2>/dev/null || true
    
    # Stop Gunicorn
    if [ -f "$PID_DIR/gunicorn.pid" ]; then
        kill $(cat "$PID_DIR/gunicorn.pid") 2>/dev/null || true
        rm "$PID_DIR/gunicorn.pid"
    fi
    
    print_success "Services stopped"
}

# Function to show status
show_status() {
    print_status "Service Status:"
    
    # Check MySQL
    if brew services list | grep mysql | grep started > /dev/null; then
        print_success "MySQL: Running"
    else
        print_error "MySQL: Not running"
    fi
    
    # Check Nginx
    if pgrep nginx > /dev/null; then
        print_success "Nginx: Running"
    else
        print_error "Nginx: Not running"
    fi
    
    # Check Gunicorn
    if [ -f "$PID_DIR/gunicorn.pid" ] && kill -0 $(cat "$PID_DIR/gunicorn.pid") 2>/dev/null; then
        print_success "Gunicorn: Running"
    else
        print_error "Gunicorn: Not running"
    fi
}

# Function to show logs
show_logs() {
    print_status "Recent logs:"
    
    if [ -f "$LOG_DIR/error.log" ]; then
        tail -n 20 "$LOG_DIR/error.log"
    else
        print_warning "No error logs found"
    fi
}

# Function to show usage
usage() {
    echo "Usage: $0 [command]"
    echo "Commands:"
    echo "  deploy    - Full setup (default)"
    echo "  start     - Start services"
    echo "  stop      - Stop services"
    echo "  restart   - Restart services"
    echo "  status    - Show service status"
    echo "  logs      - Show application logs"
}

# Handle command line arguments
case "${1:-deploy}" in
    deploy)
        deploy
        ;;
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        stop_services
        sleep 2
        start_services
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    *)
        usage
        exit 1
        ;;
esac 