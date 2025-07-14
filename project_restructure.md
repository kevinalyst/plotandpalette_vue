# Project Restructure Plan

## Current Issues to Address:
- Too many overlapping technologies (Node.js + Python + Docker + Vue.js)
- Complex Docker setup for simple deployment
- No database integration
- Missing production web server

## New 4-Component Architecture:

### 1. **Nginx** (Web Server + Reverse Proxy)
- Serves static files (HTML, CSS, JS, images)
- Proxies API requests to Python backend
- Handles SSL termination
- Load balancing if needed

### 2. **Frontend** (Static Files)
- `index.html` - Main interface
- `styles.css` - All styling
- `script.js` - Client-side logic
- `image/` - Static assets
- `uploads/` - User uploaded files

### 3. **Backend** (Python Flask + Gunicorn)
- `server.py` - Flask application
- `recommendation_service_embedded.py` - ML pipeline
- `story_generation/` - Story generation logic
- Gunicorn WSGI server for production

### 4. **Database** (MySQL)
- User sessions and selections
- Palette metadata
- Recommendation history
- Story generation logs

## Files to Keep:
✅ index.html
✅ styles.css  
✅ script.js
✅ server.py
✅ recommendation_service_embedded.py
✅ story_generation/
✅ image/
✅ uploads/
✅ requirements.txt

## Files to Remove:
❌ server.js (Node.js - replaced by server.py)
❌ package.json, package-lock.json (Node.js)
❌ docker-compose.yml, Dockerfile* (Docker complexity)
❌ vue-project/ (Vue.js - replaced by static frontend)
❌ node_modules/ (Node.js)
❌ one-click-start.sh (Docker startup)
❌ All .md documentation files
❌ .dockerignore
❌ Various log files

## New Files to Create:
🆕 nginx.conf - Nginx configuration
🆕 gunicorn.conf.py - Gunicorn configuration  
🆕 database.py - MySQL integration
🆕 deploy.sh - Deployment script
🆕 requirements-prod.txt - Production dependencies 