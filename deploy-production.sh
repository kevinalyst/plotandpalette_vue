#!/bin/bash

# Plot & Palette - Production Deployment Script
# ============================================
# This script deploys the application to production with SSL certificates

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DOMAIN="plotandpalette.uk"
EMAIL="your-email@example.com"  # Replace with your email
PROJECT_DIR="$(pwd)"

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

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please run vm-setup.sh first."
        exit 1
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed. Please run vm-setup.sh first."
        exit 1
    fi
    
    # Check if production environment file exists
    if [ ! -f "docker.env.prod" ]; then
        log_error "docker.env.prod file not found. Please create it with your configuration."
        exit 1
    fi
    
    # Check if API key is set
    if grep -q "your_anthropic_api_key_here" docker.env.prod; then
        log_error "Please update ANTHROPIC_API_KEY in docker.env.prod with your actual API key."
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Check DNS configuration
check_dns() {
    log_info "Checking DNS configuration..."
    
    DOMAIN_IP=$(dig +short $DOMAIN)
    EXPECTED_IP="34.39.28.3"
    
    if [ "$DOMAIN_IP" != "$EXPECTED_IP" ]; then
        log_warning "DNS may not be configured correctly."
        log_warning "Expected: $EXPECTED_IP"
        log_warning "Got: $DOMAIN_IP"
        log_warning "Please ensure $DOMAIN points to $EXPECTED_IP"
        
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        log_success "DNS configuration verified"
    fi
}

# Setup environment
setup_environment() {
    log_info "Setting up production environment..."
    
    # Copy production environment file
    cp docker.env.prod .env
    
    # Update email in production config if needed
    if [ "$EMAIL" != "your-email@example.com" ]; then
        sed -i "s/your-email@example.com/$EMAIL/g" docker-compose.prod.yml
    fi
    
    log_success "Environment configured"
}

# Build application images
build_images() {
    log_info "Building application images..."
    
    # Build all images
    docker-compose -f docker-compose.prod.yml build --no-cache
    
    log_success "Images built successfully"
}

# Setup SSL certificates (Let's Encrypt)
setup_ssl() {
    log_info "Setting up SSL certificates..."
    
    # Start nginx first to handle ACME challenge
    log_info "Starting nginx for ACME challenge..."
    docker-compose -f docker-compose.prod.yml up -d nginx
    
    # Wait for nginx to be ready
    sleep 10
    
    # Stop nginx to obtain certificates
    docker-compose -f docker-compose.prod.yml stop nginx
    
    # Create webroot directory
    mkdir -p ./frontend-vue/dist/.well-known/acme-challenge
    
    # Obtain SSL certificates
    log_info "Obtaining SSL certificates from Let's Encrypt..."
    docker run --rm \
        -v /etc/letsencrypt:/etc/letsencrypt \
        -v /var/lib/letsencrypt:/var/lib/letsencrypt \
        -v $(pwd)/frontend-vue/dist:/var/www/html \
        certbot/certbot:latest \
        certonly --webroot \
        --webroot-path=/var/www/html \
        --email $EMAIL \
        --agree-tos \
        --no-eff-email \
        -d $DOMAIN \
        -d www.$DOMAIN
    
    # Set proper permissions
    sudo chown -R $USER:$USER /etc/letsencrypt
    
    log_success "SSL certificates obtained"
}

# Setup SSL certificate renewal
setup_ssl_renewal() {
    log_info "Setting up SSL certificate auto-renewal..."
    
    # Create renewal script
    sudo tee /etc/cron.d/certbot-renew > /dev/null <<EOF
# Renew SSL certificates for Plot & Palette
0 2 * * * root /usr/bin/docker run --rm -v /etc/letsencrypt:/etc/letsencrypt -v /var/lib/letsencrypt:/var/lib/letsencrypt -v $(pwd)/frontend-vue/dist:/var/www/html certbot/certbot:latest renew --webroot --webroot-path=/var/www/html --quiet && /usr/bin/docker-compose -f $PROJECT_DIR/docker-compose.prod.yml restart nginx
EOF
    
    log_success "SSL auto-renewal configured"
}

# Deploy application
deploy_application() {
    log_info "Deploying application..."
    
    # Start all services
    docker-compose -f docker-compose.prod.yml up -d
    
    # Wait for services to be ready
    log_info "Waiting for services to start..."
    sleep 30
    
    # Check service health
    check_service_health
    
    log_success "Application deployed successfully"
}

# Check service health
check_service_health() {
    log_info "Checking service health..."
    
    # Wait for services to be fully ready
    max_attempts=30
    attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        log_info "Health check attempt $attempt/$max_attempts..."
        
        # Check if all containers are running
        if docker-compose -f docker-compose.prod.yml ps | grep -q "Exit"; then
            log_warning "Some containers have exited, attempt $attempt/$max_attempts"
        else
            # Check HTTP health endpoint
            if curl -f http://localhost/health > /dev/null 2>&1; then
                log_success "All services are healthy"
                return 0
            fi
        fi
        
        sleep 10
        attempt=$((attempt + 1))
    done
    
    log_error "Health check failed after $max_attempts attempts"
    log_info "Showing container status:"
    docker-compose -f docker-compose.prod.yml ps
    
    log_info "Showing logs:"
    docker-compose -f docker-compose.prod.yml logs --tail=20
    
    return 1
}

# Show deployment info
show_deployment_info() {
    log_success "=================================="
    log_success "🎉 DEPLOYMENT COMPLETED!"
    log_success "=================================="
    log_info "Application URLs:"
    log_info "  • HTTP:  http://$DOMAIN"
    log_info "  • HTTPS: https://$DOMAIN"
    log_info "  • Health: https://$DOMAIN/health"
    echo
    log_info "Service Status:"
    docker-compose -f docker-compose.prod.yml ps
    echo
    log_info "Useful Commands:"
    log_info "  • View logs: docker-compose -f docker-compose.prod.yml logs -f"
    log_info "  • Restart:   docker-compose -f docker-compose.prod.yml restart"
    log_info "  • Stop:      docker-compose -f docker-compose.prod.yml down"
    log_info "  • Update:    git pull && docker-compose -f docker-compose.prod.yml up -d --build"
    echo
    log_warning "Remember to:"
    log_warning "  • Test all functionality on the live site"
    log_warning "  • Monitor logs for any issues"
    log_warning "  • Set up monitoring and backups"
}

# Handle errors
handle_error() {
    log_error "Deployment failed!"
    log_info "Cleaning up..."
    docker-compose -f docker-compose.prod.yml down || true
    exit 1
}

# Set error trap
trap handle_error ERR

# Main deployment function
main() {
    log_info "Starting production deployment for Plot & Palette..."
    log_info "Domain: $DOMAIN"
    log_info "VM IP: 34.39.28.3"
    
    check_prerequisites
    check_dns
    setup_environment
    build_images
    
    # Ask about SSL certificates
    read -p "Do you want to obtain SSL certificates from Let's Encrypt? (Y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Nn]$ ]]; then
        log_warning "Skipping SSL certificate setup. Application will use self-signed certificates."
    else
        setup_ssl
        setup_ssl_renewal
    fi
    
    deploy_application
    show_deployment_info
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --email)
            EMAIL="$2"
            shift 2
            ;;
        --domain)
            DOMAIN="$2"
            shift 2
            ;;
        --skip-ssl)
            SKIP_SSL=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --email EMAIL     Email for SSL certificates"
            echo "  --domain DOMAIN   Domain name (default: plotandpalette.uk)"
            echo "  --skip-ssl        Skip SSL certificate setup"
            echo "  -h, --help        Show this help"
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Run main function
main "$@" 