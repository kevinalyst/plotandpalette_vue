#!/bin/bash

# Plot & Palette - Google Cloud VM Setup Script
# ============================================
# This script sets up the production environment on Google Cloud VM
# VM IP: 34.39.82.238
# Domain: plotandpalette.uk

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        log_error "This script should not be run as root. Please run as a regular user with sudo privileges."
        exit 1
    fi
}

# Update system packages
update_system() {
    log_info "Updating system packages..."
    sudo apt-get update -y
    sudo apt-get upgrade -y
}

# Install Docker
install_docker() {
    log_info "Installing Docker..."
    
    # Remove old Docker packages
    sudo apt-get remove -y docker docker-engine docker.io containerd runc || true
    
    # Install prerequisites
    sudo apt-get install -y \
        apt-transport-https \
        ca-certificates \
        curl \
        gnupg \
        lsb-release
    
    # Add Docker GPG key
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    
    # Add Docker repository
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Install Docker
    sudo apt-get update -y
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io
    
    # Add user to docker group
    sudo usermod -aG docker $USER
    
    # Enable Docker service
    sudo systemctl enable docker
    sudo systemctl start docker
    
    log_success "Docker installed successfully"
}

# Install Docker Compose
install_docker_compose() {
    log_info "Installing Docker Compose..."
    
    # Download Docker Compose
    DOCKER_COMPOSE_VERSION="2.21.0"
    sudo curl -L "https://github.com/docker/compose/releases/download/v${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    
    # Make it executable
    sudo chmod +x /usr/local/bin/docker-compose
    
    # Create symlink for docker-compose command
    sudo ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose
    
    log_success "Docker Compose installed successfully"
}

# Install Git
install_git() {
    log_info "Installing Git..."
    sudo apt-get install -y git
    log_success "Git installed successfully"
}

# Install additional tools
install_tools() {
    log_info "Installing additional tools..."
    sudo apt-get install -y \
        curl \
        wget \
        vim \
        nano \
        htop \
        ufw \
        fail2ban \
        certbot \
        python3-certbot-nginx
    
    log_success "Additional tools installed successfully"
}

# Configure firewall
configure_firewall() {
    log_info "Configuring firewall..."
    
    # Enable UFW
    sudo ufw --force enable
    
    # Allow SSH
    sudo ufw allow ssh
    
    # Allow HTTP and HTTPS
    sudo ufw allow 80/tcp
    sudo ufw allow 443/tcp
    
    # Allow specific application ports (for debugging if needed)
    sudo ufw allow 5003/tcp comment "Backend API"
    
    # Show status
    sudo ufw status verbose
    
    log_success "Firewall configured successfully"
}

# Create project directories
create_directories() {
    log_info "Creating project directories..."
    
    mkdir -p ~/plotandpalette/{logs,uploads,ssl}
    mkdir -p ~/plotandpalette/logs/{nginx,application}
    
    log_success "Project directories created successfully"
}

# Configure fail2ban for security
configure_fail2ban() {
    log_info "Configuring fail2ban..."
    
    # Create custom jail configuration
    sudo tee /etc/fail2ban/jail.local > /dev/null <<EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true
port = ssh
logpath = /var/log/auth.log
maxretry = 3

[nginx-http-auth]
enabled = true
filter = nginx-http-auth
port = http,https
logpath = /var/log/nginx/error.log

[nginx-noscript]
enabled = true
port = http,https
filter = nginx-noscript
logpath = /var/log/nginx/access.log
maxretry = 6

[nginx-badbots]
enabled = true
port = http,https
filter = nginx-badbots
logpath = /var/log/nginx/access.log
maxretry = 2

[nginx-noproxy]
enabled = true
port = http,https
filter = nginx-noproxy
logpath = /var/log/nginx/access.log
maxretry = 2
EOF

    # Restart fail2ban
    sudo systemctl enable fail2ban
    sudo systemctl restart fail2ban
    
    log_success "Fail2ban configured successfully"
}

# Set up swapfile for better performance
setup_swap() {
    log_info "Setting up swap file..."
    
    # Check if swap already exists
    if swapon --show | grep -q "/swapfile"; then
        log_warning "Swap file already exists, skipping..."
        return
    fi
    
    # Create 2GB swap file
    sudo fallocate -l 2G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    
    # Make it permanent
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
    
    log_success "Swap file configured successfully"
}

# Main installation function
main() {
    log_info "Starting Plot & Palette VM setup on Google Cloud..."
    log_info "VM IP: 34.39.82.238"
    log_info "Domain: plotandpalette.uk"
    
    check_root
    update_system
    install_git
    install_docker
    install_docker_compose
    install_tools
    configure_firewall
    create_directories
    configure_fail2ban
    setup_swap
    
    log_success "==================================="
    log_success "VM Setup completed successfully!"
    log_success "==================================="
    log_warning "IMPORTANT NEXT STEPS:"
    log_warning "1. Log out and log back in to apply Docker group membership"
    log_warning "2. Clone your Git repository to ~/plotandpalette/"
    log_warning "3. Update docker.env.prod with your API keys"
    log_warning "4. Configure DNS: Point plotandpalette.uk to 34.39.82.238"
    log_warning "5. Run the deployment script: ./deploy-production.sh"
}

# Run main function
main "$@" 