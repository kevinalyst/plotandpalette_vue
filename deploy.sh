#!/bin/bash
# Plot & Palette - Production Deployment Script

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="plot-palette"
PROJECT_DIR="/var/www/plot-palette"
BACKUP_DIR="/var/backups/plot-palette"
LOG_DIR="/var/log/plot-palette"
PID_DIR="/var/run/plot-palette"
USER="www-data"
GROUP="www-data"

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

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "This script must be run as root (use sudo)"
        exit 1
    fi
}

# Install system dependencies
install_system_deps() {
    print_status "Installing system dependencies..."
    
    apt update
    apt install -y \
        nginx \
        python3 \
        python3-pip \
        python3-venv \
        python3-dev \
        build-essential \
        pkg-config \
        libmysqlclient-dev \
        curl \
        git \
        supervisor \
        certbot \
        python3-certbot-nginx
    
    print_success "System dependencies installed"
}

# Test external database connection
test_database_connection() {
    print_status "Testing external database connection..."
    
    cd $PROJECT_DIR
    source venv/bin/activate
    
    # Set environment variables
    export DB_HOST="34.142.53.204"
    export DB_USER="root"
    export DB_PASSWORD="Lihanwen1997"
    export DB_NAME="plotpalette-mydb"
    export DB_PORT="3306"
    
    # Test database connection
    python3 -c "
from database import db
try:
    if db.health_check():
        print('Database connection successful')
    else:
        print('Database connection failed')
        exit(1)
except Exception as e:
    print(f'Error connecting to database: {e}')
    exit(1)
"
    
    deactivate
    
    print_success "External database connection verified"
}

# Create project directories
create_directories() {
    print_status "Creating project directories..."
    
    mkdir -p $PROJECT_DIR
    mkdir -p $BACKUP_DIR
    mkdir -p $LOG_DIR
    mkdir -p $PID_DIR
    mkdir -p $PROJECT_DIR/uploads
    
    chown -R $USER:$GROUP $PROJECT_DIR
    chown -R $USER:$GROUP $LOG_DIR
    chown -R $USER:$GROUP $PID_DIR
    
    chmod 755 $PROJECT_DIR
    chmod 755 $PROJECT_DIR/uploads
    chmod 755 $LOG_DIR
    chmod 755 $PID_DIR
    
    print_success "Directories created"
}

# Setup Python environment
setup_python_env() {
    print_status "Setting up Python virtual environment..."
    
    cd $PROJECT_DIR
    
    # Create virtual environment
    python3 -m venv venv
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install production requirements
    if [ -f "requirements-prod.txt" ]; then
        pip install -r requirements-prod.txt
    else
        print_warning "requirements-prod.txt not found, installing basic requirements"
        pip install flask gunicorn mysql-connector-python
    fi
    
    deactivate
    
    print_success "Python environment configured"
}

# Configure Nginx
configure_nginx() {
    print_status "Configuring Nginx..."
    
    # Copy nginx configuration
    if [ -f "$PROJECT_DIR/nginx.conf" ]; then
        cp $PROJECT_DIR/nginx.conf /etc/nginx/sites-available/$PROJECT_NAME
        ln -sf /etc/nginx/sites-available/$PROJECT_NAME /etc/nginx/sites-enabled/
        rm -f /etc/nginx/sites-enabled/default
    else
        print_warning "nginx.conf not found in project directory"
    fi
    
    # Test nginx configuration
    nginx -t
    
    # Start and enable nginx
    systemctl start nginx
    systemctl enable nginx
    
    print_success "Nginx configured"
}

# Configure Supervisor for Gunicorn
configure_supervisor() {
    print_status "Configuring Supervisor for Gunicorn..."
    
    cat > /etc/supervisor/conf.d/$PROJECT_NAME.conf <<EOF
[program:$PROJECT_NAME]
command=$PROJECT_DIR/venv/bin/gunicorn -c $PROJECT_DIR/gunicorn.conf.py server:app
directory=$PROJECT_DIR
user=$USER
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=$LOG_DIR/supervisor.log
environment=FLASK_ENV="production",PYTHONPATH="$PROJECT_DIR"
EOF
    
    # Update supervisor
    supervisorctl reread
    supervisorctl update
    
    print_success "Supervisor configured"
}

# Initialize database
init_database() {
    print_status "Initializing database..."
    
    cd $PROJECT_DIR
    source venv/bin/activate
    
    # Set environment variables
    export DB_HOST="34.142.53.204"
    export DB_USER="root"
    export DB_PASSWORD="Lihanwen1997"
    export DB_NAME="plotpalette-mydb"
    
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

# Create systemd service files
create_systemd_services() {
    print_status "Creating systemd service files..."
    
    # Create plot-palette service
    cat > /etc/systemd/system/$PROJECT_NAME.service <<EOF
[Unit]
Description=Plot & Palette Web Application
After=network.target

[Service]
Type=simple
User=$USER
Group=$GROUP
WorkingDirectory=$PROJECT_DIR
Environment=FLASK_ENV=production
Environment=PYTHONPATH=$PROJECT_DIR
ExecStart=$PROJECT_DIR/venv/bin/gunicorn -c $PROJECT_DIR/gunicorn.conf.py server:app
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    systemctl daemon-reload
    systemctl enable $PROJECT_NAME.service
    
    print_success "Systemd services created"
}

# Set up SSL with Let's Encrypt (optional)
setup_ssl() {
    read -p "Do you want to set up SSL with Let's Encrypt? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "Enter your domain name: " domain
        read -p "Enter your email address: " email
        
        print_status "Setting up SSL certificate for $domain..."
        
        certbot --nginx -d $domain --email $email --agree-tos --no-eff-email
        
        print_success "SSL certificate configured"
    fi
}

# Create environment file
create_env_file() {
    print_status "Creating environment configuration..."
    
    cat > $PROJECT_DIR/.env <<EOF
# Production Environment Configuration
FLASK_ENV=production
FLASK_DEBUG=False

# External Database Configuration
DB_HOST=34.142.53.204
DB_USER=root
DB_PASSWORD=Lihanwen1997
DB_NAME=plotpalette-mydb
DB_PORT=3306

# Security
SECRET_KEY=$(openssl rand -hex 32)

# Logging
LOG_LEVEL=INFO

# Application
UPLOAD_FOLDER=/var/www/plot-palette/uploads
MAX_CONTENT_LENGTH=52428800
EOF
    
    chmod 640 $PROJECT_DIR/.env
    chown $USER:$GROUP $PROJECT_DIR/.env
    
    print_success "Environment file created"
}

# Setup log rotation
setup_log_rotation() {
    print_status "Setting up log rotation..."
    
    cat > /etc/logrotate.d/$PROJECT_NAME <<EOF
$LOG_DIR/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 $USER $GROUP
    postrotate
        systemctl reload $PROJECT_NAME
    endscript
}
EOF
    
    print_success "Log rotation configured"
}

# Main deployment function
deploy() {
    print_status "Starting Plot & Palette deployment..."
    
    check_root
    install_system_deps
    create_directories
    
    # Copy project files (assumes current directory has the project)
    if [ "$(pwd)" != "$PROJECT_DIR" ]; then
        print_status "Copying project files..."
        cp -r . $PROJECT_DIR/
        chown -R $USER:$GROUP $PROJECT_DIR
    fi
    
    setup_python_env
    create_env_file
    test_database_connection
    init_database
    configure_nginx
    configure_supervisor
    create_systemd_services
    setup_log_rotation
    
    # Start services
    print_status "Starting services..."
    systemctl start $PROJECT_NAME
    systemctl reload nginx
    supervisorctl start $PROJECT_NAME
    
    setup_ssl
    
    print_success "Deployment completed successfully!"
    print_status "Your Plot & Palette application should now be running"
    print_status "Nginx: http://your-domain.com"
    print_status "Backend: http://127.0.0.1:5000"
    print_warning "Remember to:"
    print_warning "1. Change default passwords"
    print_warning "2. Configure your domain in nginx.conf"
    print_warning "3. Set up proper backups"
    print_warning "4. Configure firewall rules"
}

# Cleanup function to remove old files
cleanup() {
    print_status "Cleaning up old files..."
    
    # Remove Node.js and Docker files
    rm -f $PROJECT_DIR/server.js
    rm -f $PROJECT_DIR/package.json
    rm -f $PROJECT_DIR/package-lock.json
    rm -f $PROJECT_DIR/docker-compose.yml
    rm -f $PROJECT_DIR/Dockerfile*
    rm -f $PROJECT_DIR/.dockerignore
    rm -f $PROJECT_DIR/one-click-start.sh
    rm -rf $PROJECT_DIR/node_modules
    rm -rf $PROJECT_DIR/vue-project
    rm -f $PROJECT_DIR/*.log
    rm -f $PROJECT_DIR/*.md
    
    print_success "Cleanup completed"
}

# Function to show usage
usage() {
    echo "Usage: $0 [command]"
    echo "Commands:"
    echo "  deploy    - Full deployment"
    echo "  cleanup   - Remove old/unnecessary files"
    echo "  restart   - Restart services"
    echo "  status    - Show service status"
    echo "  logs      - Show application logs"
}

# Handle command line arguments
case "${1:-deploy}" in
    deploy)
        deploy
        ;;
    cleanup)
        cleanup
        ;;
    restart)
        print_status "Restarting services..."
        systemctl restart $PROJECT_NAME
        systemctl reload nginx
        supervisorctl restart $PROJECT_NAME
        print_success "Services restarted"
        ;;
    status)
        echo "=== Service Status ==="
        systemctl status $PROJECT_NAME --no-pager
        systemctl status nginx --no-pager
        supervisorctl status $PROJECT_NAME
        ;;
    logs)
        echo "=== Application Logs ==="
        tail -n 50 $LOG_DIR/error.log
        ;;
    *)
        usage
        exit 1
        ;;
esac 