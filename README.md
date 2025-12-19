# 🎨 Plot & Palette

An interactive web application that analyzes color palettes and generates emotion-driven stories and art recommendations.

---

## 📁 Repository Structure

```
plotandpalette_vue/
├── apps/
│   ├── frontend/          # Vue.js SPA
│   └── api/               # Flask backend + microservices
│       ├── server.py
│       ├── database.py
│       ├── emotions_generation/
│       ├── painting_recommendation/
│       └── story_generation/
├── infra/
│   └── docker/
│       └── nginx/         # Nginx reverse proxy configs
├── data/
│   ├── schemas/           # Database schema (init.sql)
│   ├── migrations/        # Future migrations
│   └── seed/              # Future seed data
├── docs/                  # Documentation
├── archive/               # Old deployment scripts (reference only)
├── docker-compose.yml     # 👈 THE way to run local dev
└── docker.env.example     # Environment template
```

---

## 🚀 Local Development (THE One Way™)

### Prerequisites
- Docker & Docker Compose installed
- 8GB+ RAM recommended

### Step 1: Setup Environment
```bash
# Copy environment template
cp docker.env.example docker.env

# Edit docker.env and add your OpenAI API key (optional for testing)
# OPENAI_API_KEY=your_key_here
```

### Step 2: Run Everything
```bash
# Start all services (database, backend, frontend, nginx)
docker-compose up -d

# View logs
docker-compose logs -f

# Stop everything
docker-compose down

# Stop and remove database volume (fresh start)
docker-compose down -v
```

### Step 3: Access the App
- **Frontend**: http://localhost:8081
- **Backend API**: http://localhost:5003
- **Story API**: http://localhost:5002
- **Nginx (reverse proxy)**: http://localhost:80

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│         Nginx (Port 80)                 │
│    Reverse Proxy & Static Files         │
└─────────────────┬───────────────────────┘
                  │
    ┌─────────────┼─────────────┐
    │             │             │
    ▼             ▼             ▼
┌─────────┐  ┌─────────┐  ┌─────────┐
│  Vue.js │  │  Flask  │  │  Story  │
│Frontend │  │ Backend │  │   API   │
│  :8081  │  │  :5003  │  │  :5002  │
└─────────┘  └────┬────┘  └─────────┘
                  │
                  ▼
            ┌──────────┐
            │  MySQL   │
            │  :3306   │
            └──────────┘
```

---

## 🔧 Key Services

### Database (MySQL 8.0)
- **Container**: `plot-palette-db`
- **Port**: 3306
- **Credentials**: See `docker.env.example`
- **Schema**: Auto-initialized from `data/schemas/init.sql`

### Backend (Flask)
- **Container**: `plot-palette-backend`
- **Port**: 5003
- **Includes**: Emotion prediction, painting recommendations

### Story API (Python)
- **Container**: `plot-palette-stories`
- **Port**: 5002
- **Requires**: OpenAI API key (set in `docker.env`)

### Frontend (Vue.js)
- **Container**: `plot-palette-frontend`
- **Port**: 8081
- **Built with**: Vite + Vue 3

### Nginx
- **Container**: `plot-palette-nginx`
- **Ports**: 80, 443
- **Purpose**: Reverse proxy, static file serving

---

## 📚 Documentation

See the `docs/` folder for:
- **API-Documentation.md** - API endpoints and usage
- **PRODUCTION-MIGRATION-GUIDE.md** - Cloud deployment reference
- **Database-Connection-Analysis.md** - DB schema and connections
- **DOCKER-UPDATE-REMINDER.md** - Docker best practices

---

## 🗂️ Archive

The `archive/` folder contains old deployment scripts for:
- Google Cloud Run
- GCP VM deployments

These are kept for reference but are **not actively maintained**.

---

## 🛠️ Development Commands

```bash
# Rebuild a specific service
docker-compose up -d --build backend

# View service status
docker-compose ps

# Access container shell
docker-compose exec backend bash

# View database
docker-compose exec db mysql -u root -p plotpalette-mydb

# Clean everything (including volumes)
docker-compose down -v
docker system prune -a
```

---

## 🐛 Troubleshooting

### Services won't start
```bash
# Check logs
docker-compose logs backend
docker-compose logs db

# Ensure no port conflicts
lsof -i :3306,5002,5003,8081,80
```

### Database connection issues
```bash
# Wait for MySQL to initialize (first start takes ~30s)
docker-compose logs db

# Verify database is healthy
docker-compose ps db
```

### Frontend can't reach backend
- Ensure `VITE_API_URL` in docker-compose.yml points to `http://backend:5000`
- Check backend health: `curl http://localhost:5003/health`

---

## 📝 Notes

- **First startup** takes 2-3 minutes (database initialization + image builds)
- **Database data** persists in Docker volume `mysql_data`
- **File uploads** stored in `./uploads/` (gitignored)
- **Logs** written to `./logs/` (gitignored)

---

## 🎯 Next Steps

1. Clone the repo
2. Copy `docker.env.example` → `docker.env`
3. Run `docker-compose up -d`
4. Open http://localhost:8081
5. Start building! 🎨

---

**Need help?** Check the docs/ folder or review archived deployment scripts for reference.
