#!/bin/bash
# Deploy Virtual Environment Fix (Direct Mode)
# For when running directly from the deployment directory

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="/var/www/plot-palette"
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

# Set proper permissions on server.py
fix_permissions() {
    print_status "Setting proper permissions on server.py..."
    
    chown $USER:$GROUP "$PROJECT_DIR/server.py"
    chmod 644 "$PROJECT_DIR/server.py"
    
    print_success "Permissions set correctly"
}

# Test virtual environment
test_venv() {
    print_status "Testing virtual environment..."
    
    VENV_PYTHON="$PROJECT_DIR/venv/bin/python3"
    
    if [ ! -f "$VENV_PYTHON" ]; then
        print_error "Virtual environment Python not found: $VENV_PYTHON"
        exit 1
    fi
    
    # Test pandas import
    if sudo -u $USER bash -c "cd $PROJECT_DIR && $VENV_PYTHON -c 'import pandas; print(\"pandas:\", pandas.__version__)'"; then
        print_success "pandas available in virtual environment"
    else
        print_error "pandas not available in virtual environment"
        print_status "Installing missing packages..."
        
        # Install missing packages
        sudo -u $USER bash -c "cd $PROJECT_DIR && source venv/bin/activate && pip install pandas numpy scikit-learn joblib"
        
        # Test again
        if sudo -u $USER bash -c "cd $PROJECT_DIR && $VENV_PYTHON -c 'import pandas; print(\"pandas:\", pandas.__version__)'"; then
            print_success "pandas installed successfully"
        else
            print_error "Failed to install pandas"
            exit 1
        fi
    fi
}

# Test server import
test_server() {
    print_status "Testing server import..."
    
    VENV_PYTHON="$PROJECT_DIR/venv/bin/python3"
    
    if sudo -u $USER bash -c "cd $PROJECT_DIR && timeout 10s $VENV_PYTHON -c 'import server; print(\"Server import: OK\")'"; then
        print_success "Server imports successfully"
    else
        print_warning "Server import test timed out (this is normal)"
    fi
}

# Restart systemd service
restart_service() {
    print_status "Restarting plot-palette service..."
    
    systemctl stop plot-palette.service
    sleep 2
    systemctl start plot-palette.service
    
    if systemctl is-active --quiet plot-palette.service; then
        print_success "Service restarted successfully"
    else
        print_error "Service failed to start"
        print_status "Checking service status..."
        systemctl status plot-palette.service --no-pager
        exit 1
    fi
}

# Show service logs
show_logs() {
    print_status "Showing recent service logs..."
    
    echo "=========================="
    echo "Recent service logs:"
    echo "=========================="
    journalctl -u plot-palette.service --no-pager -n 20
    echo "=========================="
}

# Test API endpoint
test_api() {
    print_status "Testing API endpoint..."
    
    sleep 5  # Give service time to start
    
    # Test health endpoint
    if curl -f http://localhost:5000/api/health > /dev/null 2>&1; then
        print_success "API health check passed"
    else
        print_error "API health check failed"
        return 1
    fi
}

# Main deployment function
main() {
    print_status "Starting Virtual Environment Fix Deployment (Direct Mode)..."
    
    check_root
    print_status "Skipping backup and copy (server.py already updated via git pull)"
    fix_permissions
    test_venv
    test_server
    restart_service
    show_logs
    test_api
    
    print_success "Deployment completed successfully!"
    print_status "The server.py now uses virtual environment Python for subprocesses"
    print_status "Monitor the logs to ensure the fix is working:"
    print_status "  sudo journalctl -u plot-palette.service -f"
}

# Run main function
main "$@"
