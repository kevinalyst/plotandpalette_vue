# 🚀 Plot & Palette - Production Migration Guide

## Overview
This guide will walk you through migrating your Plot & Palette application from localhost to a Google Cloud VM with HTTPS support using your domain `plotandpalette.uk`.

### 📋 Migration Details
- **Source**: Localhost development environment
- **Target**: Google Cloud VM (Linux)
- **VM IP**: `34.39.82.238`
- **Domain**: `plotandpalette.uk`
- **SSL**: Let's Encrypt certificates
- **Database**: Google Cloud SQL (already configured)

## 🎯 Prerequisites

### 1. Domain Configuration
**⚠️ CRITICAL: Set up DNS BEFORE starting deployment**

Configure your domain DNS records:
```
Type: A
Name: @
Value: 34.39.28.3
TTL: 300

Type: A
Name: www
Value: 34.39.28.3
TTL: 300
```

### 2. API Keys Required
- **OpenAI API Key**: For story generation
- **Email Address**: For SSL certificate registration

### 3. VM Access
- SSH access to your Google Cloud VM
- User with sudo privileges

## 📚 Migration Steps

### Step 1: Prepare Local Environment

1. **Update Production Environment File**
   ```bash
   # Edit docker.env.prod with your actual values
   nano docker.env.prod
   ```
   
   Update these critical values:
   ```env
   ANTHROPIC_API_KEY=your_actual_anthropic_api_key
   SSL_EMAIL=your-email@domain.com
   ```

2. **Commit and Push Changes**
   ```bash
   git add .
   git commit -m "Add production configurations for VM deployment"
   git push origin main
   ```

### Step 2: Set Up Google Cloud VM

1. **Connect to Your VM**
   ```bash
   ssh username@34.39.82.238
   ```

2. **Run VM Setup Script**
   ```bash
   # Download and run the setup script
   curl -fsSL https://raw.githubusercontent.com/Kevin-lee-187/plotandpalette_vue/main/vm-setup.sh -o vm-setup.sh
   chmod +x vm-setup.sh
   ./vm-setup.sh
   ```

3. **Log Out and Back In**
   ```bash
   exit
   ssh username@34.39.82.238
   ```
   This applies Docker group membership.

### Step 3: Deploy Application

1. **Clone Repository**
   ```bash
   cd ~
   git clone https://github.com/Kevin-lee-187/plotandpalette_vue.git plotandpalette
   cd plotandpalette
   ```

2. **Update Configuration**
   ```bash
   # Edit production environment file
   nano docker.env.prod
   
   # Update these values:
   # ANTHROPIC_API_KEY=your_actual_api_key
   # SSL_EMAIL=your_email@example.com
   ```

3. **Run Deployment Script**
   ```bash
   chmod +x deploy-production.sh
   ./deploy-production.sh --email your-email@example.com
   ```

### Step 4: Verify Deployment

1. **Check Service Status**
   ```bash
   docker-compose -f docker-compose.prod.yml ps
   ```

2. **Test Application**
   - HTTP: `http://plotandpalette.uk`
   - HTTPS: `https://plotandpalette.uk`
   - Health: `https://plotandpalette.uk/health`

3. **Monitor Logs**
   ```bash
   # View all logs
   docker-compose -f docker-compose.prod.yml logs -f
   
   # View specific service logs
   docker-compose -f docker-compose.prod.yml logs -f backend
   docker-compose -f docker-compose.prod.yml logs -f nginx
   ```

## 🏗️ Architecture Overview

### Production Services
```
┌─────────────────┐    ┌─────────────────┐
│     Internet    │    │   Let's Encrypt │
│                 │    │  (SSL Certs)    │
└─────────┬───────┘    └─────────────────┘
          │                      │
          ▼                      │
┌─────────────────────────────────────────┐
│           Nginx Reverse Proxy            │
│     (Port 80 → HTTPS, Port 443)        │
│        - SSL Termination                 │
│        - Static File Serving            │
│        - API Routing                    │
└─────────┬───────────────────────────────┘
          │
          ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   Vue Frontend  │  │  Flask Backend  │  │  Emotion API    │
│   (Port 8081)   │  │  (Port 5003)    │  │  (Port 5001)    │
└─────────────────┘  └─────────┬───────┘  └─────────────────┘
                               │
                               ▼
                     ┌─────────────────┐  ┌─────────────────┐
                     │   Story API     │  │ Google Cloud SQL │
                     │  (Port 5002)    │  │  (External DB)   │
                     └─────────────────┘  └─────────────────┘
```

### Network Flow
1. **User** → `plotandpalette.uk:443` (HTTPS)
2. **Nginx** → SSL termination, routing to services
3. **Frontend** → Serves Vue.js SPA
4. **Backend** → API endpoints, database connections
5. **APIs** → Emotion prediction, story generation

## 🔧 Key Configuration Files

### Production Files Created
- `docker-compose.prod.yml` - Production container orchestration
- `docker.env.prod` - Production environment variables
- `deployment/nginx/site.prod.conf` - HTTPS nginx configuration
- `deployment/nginx/Dockerfile.prod` - Production nginx image
- `frontend-vue/Dockerfile.prod` - Optimized frontend build
- `vm-setup.sh` - VM initialization script
- `deploy-production.sh` - Deployment automation

### Database Connection
Your application will continue using the same Google Cloud SQL database:
```env
DB_HOST=34.142.53.204
DB_PORT=3306
DB_NAME=plot-palette-mydb
DB_USER=root
DB_PASSWORD=Lihanwen1997
```

## 🔒 Security Features

### SSL/HTTPS
- **Let's Encrypt certificates** - Free, auto-renewing
- **HTTP → HTTPS redirect** - All traffic secured
- **Modern TLS configuration** - TLS 1.2/1.3 only
- **Security headers** - HSTS, CSP, XSS protection

### Network Security
- **UFW firewall** - Only necessary ports open
- **Fail2ban** - Brute force protection
- **Rate limiting** - API abuse prevention
- **Container isolation** - Docker network security

### Application Security
- **Environment isolation** - Production configs
- **Secret management** - API keys in environment files
- **File upload restrictions** - Secure image handling
- **CORS policies** - Proper origin restrictions

## 📊 Monitoring & Maintenance

### Health Checks
```bash
# Application health
curl https://plotandpalette.uk/health

# Container status
docker-compose -f docker-compose.prod.yml ps

# Resource usage
docker stats

# System resources
htop
df -h
free -h
```

### Log Monitoring
```bash
# Application logs
docker-compose -f docker-compose.prod.yml logs -f

# Nginx access logs
sudo tail -f /var/log/nginx/access.log

# System logs
sudo journalctl -f
```

### SSL Certificate Status
```bash
# Check certificate expiry
sudo certbot certificates

# Test renewal
sudo certbot renew --dry-run
```

## 🔄 Updates & Deployment

### Regular Updates
```bash
# Pull latest changes
cd ~/plotandpalette
git pull origin main

# Rebuild and restart
docker-compose -f docker-compose.prod.yml up -d --build

# Check status
docker-compose -f docker-compose.prod.yml ps
```

### Rolling Back
```bash
# Stop services
docker-compose -f docker-compose.prod.yml down

# Checkout previous version
git checkout HEAD~1

# Rebuild and start
docker-compose -f docker-compose.prod.yml up -d --build
```

## 🆘 Troubleshooting

### Common Issues

#### 1. SSL Certificate Issues
```bash
# Check certificate status
sudo certbot certificates

# Renew manually
sudo certbot renew --force-renewal

# Restart nginx
docker-compose -f docker-compose.prod.yml restart nginx
```

#### 2. Container Issues
```bash
# Check container logs
docker-compose -f docker-compose.prod.yml logs [service-name]

# Restart specific service
docker-compose -f docker-compose.prod.yml restart [service-name]

# Rebuild service
docker-compose -f docker-compose.prod.yml up -d --build [service-name]
```

#### 3. Database Connection Issues
```bash
# Test database connectivity from VM
mysql -h 34.142.53.204 -u root -p plot-palette-mydb

# Check backend logs for connection errors
docker-compose -f docker-compose.prod.yml logs backend
```

#### 4. DNS Issues
```bash
# Check DNS resolution
dig plotandpalette.uk
nslookup plotandpalette.uk

# Check if domain points to correct IP
ping plotandpalette.uk
```

### Emergency Procedures

#### Complete Service Restart
```bash
cd ~/plotandpalette
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d
```

#### Reset SSL Certificates
```bash
sudo rm -rf /etc/letsencrypt/live/plotandpalette.uk
sudo rm -rf /etc/letsencrypt/archive/plotandpalette.uk
sudo rm -rf /etc/letsencrypt/renewal/plotandpalette.uk.conf
./deploy-production.sh --email your-email@example.com
```

## 📞 Support Commands

### Quick Status Check
```bash
# One-line status check
echo "=== System Status ===" && \
docker-compose -f ~/plotandpalette/docker-compose.prod.yml ps && \
echo -e "\n=== SSL Status ===" && \
sudo certbot certificates && \
echo -e "\n=== Disk Usage ===" && \
df -h && \
echo -e "\n=== Memory Usage ===" && \
free -h
```

### Performance Monitoring
```bash
# Monitor resources
watch -n 2 'docker stats --no-stream'

# Monitor logs in real-time
docker-compose -f docker-compose.prod.yml logs -f --tail=50
```

## ✅ Post-Migration Checklist

- [ ] DNS points to VM IP (34.39.82.238)
- [ ] HTTPS certificate obtained and valid
- [ ] All services running and healthy
- [ ] Database connection working
- [ ] File uploads functioning
- [ ] Story generation working
- [ ] Emotion prediction working
- [ ] SSL auto-renewal configured
- [ ] Firewall configured properly
- [ ] Monitoring set up
- [ ] Backup strategy planned

## 🎉 Success Validation

Your migration is successful when:

1. **🌐 Website loads**: `https://plotandpalette.uk`
2. **🔒 SSL certificate valid**: Green lock in browser
3. **⚡ All features work**: Upload, analyze, generate stories
4. **📊 Health check passes**: `https://plotandpalette.uk/health`
5. **🔄 Auto-redirect works**: `http://` → `https://`

---

**🎨 Welcome to production! Your Plot & Palette application is now live at `https://plotandpalette.uk`** 