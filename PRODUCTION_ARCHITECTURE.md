# Plot & Palette - Production Architecture

## 🏗️ **4-Component Production Architecture**

Your Plot & Palette application has been restructured into **4 essential production components**:

### 1. **Nginx** (Web Server + Reverse Proxy)
- **Port**: 80/443
- **Role**: Front door for all requests
- **Responsibilities**:
  - Serves static files (HTML, CSS, JS, images)
  - SSL termination
  - Compression (gzip)
  - Caching headers
  - Security headers
  - Reverse proxy to Python backend

### 2. **Frontend** (Static Files)
- **Files**: `index.html`, `styles.css`, `script.js`
- **Assets**: `image/`, `uploads/`, `palette GIF/`, `15 emotion illustrations/`
- **Role**: User interface served by Nginx
- **Technology**: Vanilla HTML/CSS/JavaScript (removed Vue.js complexity)

### 3. **Backend** (Python Flask + Gunicorn)
- **Port**: 5000 (internal)
- **Technology**: Flask + Gunicorn WSGI server
- **Files**: `server.py`, `recommendation_service_embedded.py`, `story_generation/`
- **Role**: Application logic, ML processing, API endpoints

### 4. **Database** (MySQL)
- **Port**: 3306 (internal)
- **Role**: Persistent data storage
- **Tables**: users, palettes, recommendations, user_selections, stories, analytics

---

## 📁 **Clean File Structure**

### **Essential Files (Keep)**
```
plot-palette/
├── index.html                          # Main frontend
├── styles.css                         # All styling
├── script.js                          # Frontend logic
├── server.py                          # Python backend
├── database.py                        # MySQL integration
├── recommendation_service_embedded.py  # ML pipeline
├── requirements-prod.txt               # Python dependencies
├── nginx.conf                         # Web server config
├── gunicorn.conf.py                   # WSGI server config
├── deploy.sh                          # Deployment script
├── story_generation/                  # AI story features
├── image/                             # Static assets
├── uploads/                           # User uploads
├── palette GIF/                       # Animation assets
└── 15 emotion illustrations/          # Emotion assets
```

### **Files Removed**
- ❌ `server.js` (Node.js backend)
- ❌ `package.json`, `package-lock.json` (Node.js)
- ❌ `docker-compose.yml`, `Dockerfile*` (Docker)
- ❌ `vue-project/` (Vue.js frontend)
- ❌ `node_modules/` (Node.js dependencies)
- ❌ All `.md` documentation files
- ❌ Various log files

---

## 🚀 **Deployment Process**

### **1. Automated Deployment**
```bash
# Make deployment script executable
chmod +x deploy.sh

# Full production deployment
sudo ./deploy.sh deploy

# Clean up old files
sudo ./deploy.sh cleanup
```

### **2. Manual Setup Steps**

#### **System Requirements**
- Ubuntu/Debian Linux server
- Python 3.8+
- MySQL 8.0+
- Nginx
- Sudo access

#### **Environment Variables**
Create `.env` file:
```bash
FLASK_ENV=production
DB_HOST=localhost
DB_USER=plot_palette_user
DB_PASSWORD=your_secure_password
DB_NAME=plot_palette
SECRET_KEY=your_secret_key
```

#### **Database Setup**
```sql
CREATE DATABASE plot_palette CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'plot_palette_user'@'localhost' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON plot_palette.* TO 'plot_palette_user'@'localhost';
FLUSH PRIVILEGES;
```

---

## ⚙️ **Service Management**

### **Start Services**
```bash
# Start all services
sudo systemctl start plot-palette
sudo systemctl start nginx
sudo systemctl start mysql

# Enable auto-start on boot
sudo systemctl enable plot-palette
sudo systemctl enable nginx
sudo systemctl enable mysql
```

### **Monitor Services**
```bash
# Check service status
sudo ./deploy.sh status

# View logs
sudo ./deploy.sh logs

# Restart services
sudo ./deploy.sh restart
```

### **Service Architecture**
```
Internet → Nginx (80/443) → Gunicorn (5000) → Flask App
                         ↘
                           MySQL (3306)
```

---

## 🔒 **Security Features**

### **Nginx Security**
- Security headers (XSS, CSRF protection)
- File type restrictions
- Access control for sensitive files
- SSL/TLS encryption ready
- Rate limiting capability

### **Application Security**
- Environment-based configuration
- Secure session management
- Input validation
- SQL injection protection
- File upload restrictions

### **Database Security**
- Dedicated database user
- Limited privileges
- Connection encryption
- Backup encryption

---

## 📊 **Database Schema**

### **Core Tables**
- **users**: Session tracking and user management
- **palettes**: Uploaded color palettes with metadata
- **recommendations**: ML-generated painting recommendations
- **user_selections**: User's painting choices
- **stories**: Generated stories with narratives
- **analytics**: Usage tracking and behavior analysis

### **Data Flow**
1. User uploads palette → `palettes` table
2. ML generates recommendations → `recommendations` table
3. User selects paintings → `user_selections` table
4. AI generates story → `stories` table
5. All interactions → `analytics` table

---

## 🔧 **Configuration Files**

### **Nginx** (`nginx.conf`)
- Static file serving with caching
- API proxy to Python backend
- Security headers and compression
- SSL configuration ready

### **Gunicorn** (`gunicorn.conf.py`)
- Multi-worker configuration
- Optimized for ML workloads
- Logging and monitoring
- Process management

### **Python Requirements** (`requirements-prod.txt`)
- Flask web framework
- Gunicorn WSGI server
- MySQL connector
- ML libraries (pandas, scikit-learn)
- AI libraries (anthropic)

---

## 🎯 **Benefits of New Architecture**

### **Simplified Technology Stack**
- ✅ Single language (Python) for backend
- ✅ Standard web server (Nginx)
- ✅ Proven database (MySQL)
- ✅ No Docker complexity

### **Production Ready**
- ✅ Horizontal scaling with Gunicorn workers
- ✅ Database persistence
- ✅ Proper logging and monitoring
- ✅ SSL/HTTPS support
- ✅ Automated deployment

### **Performance Optimized**
- ✅ Static file caching
- ✅ Gzip compression
- ✅ Database indexing
- ✅ Efficient ML processing
- ✅ Connection pooling

### **Maintainable**
- ✅ Clear separation of concerns
- ✅ Standard deployment patterns
- ✅ Comprehensive logging
- ✅ Easy scaling and updates
- ✅ Version control friendly

---

## 🌐 **DNS and Domain Setup**

### **Domain Configuration**
1. Point your domain A record to server IP
2. Update `nginx.conf` with your domain name
3. Run `sudo ./deploy.sh` and choose SSL setup
4. Automatic Let's Encrypt SSL certificate

### **Final URLs**
- **Website**: `https://your-domain.com`
- **API**: `https://your-domain.com/api/`
- **Health Check**: `https://your-domain.com/api/health`

---

## 🔄 **Maintenance Tasks**

### **Regular Maintenance**
```bash
# Update system packages
sudo apt update && sudo apt upgrade

# Restart services
sudo ./deploy.sh restart

# Check logs
sudo ./deploy.sh logs

# Database backup
mysqldump -u plot_palette_user -p plot_palette > backup.sql
```

### **Monitoring**
- Service health: `/api/health`
- Log files: `/var/log/plot-palette/`
- Database queries: MySQL slow query log
- Resource usage: `htop`, `iotop`

---

Your Plot & Palette application is now production-ready with a clean, scalable, and maintainable architecture! 🎨 