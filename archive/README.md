# 📦 Archive

This folder contains **deprecated deployment scripts** from previous cloud infrastructure setups. These files are kept for reference but are **not actively maintained** and should not be used for new deployments.

---

## 🗂️ Archived Files

### Google Cloud Run Deployment
- **cloudrun.build.push.sh** - Builds and pushes Docker images to Google Artifact Registry
- **cloudrun.deploy.sh** - Deploys application to Google Cloud Run
- **service.cloudrun.yaml** - Cloud Run service configuration (K8s manifest)

### Google Cloud VM Deployment
- **deploy-production.sh** - Full production deployment script for GCP VM
- **vm-setup.sh** - Initial VM setup (Docker, nginx, SSL, firewall)
- **docker-compose.prod.yml** - Production docker-compose with Cloud SQL connection
- **docker.env.prod** - Production environment variables

### Old Setup
- **setup.sh** - Original setup script (replaced by docker-compose workflow)

---

## 🚫 Why Archived?

These scripts were built for specific cloud infrastructure that is no longer the primary deployment target:

1. **Cloud Run** - Serverless container platform (expensive, complex multi-container setup)
2. **GCP VM** - Self-managed VM with manual SSL setup (operational overhead)
3. **External Cloud SQL** - Managed MySQL instance (cost + network latency)

The current local development setup uses:
- ✅ **docker-compose** with local MySQL
- ✅ Simpler, faster, free for development
- ✅ Easy to transition to modern platforms (Cloudflare, Vercel, Railway, etc.)

---

## 📚 Reference Value

These files may still be useful for:
- Understanding previous infrastructure decisions
- Migrating to similar cloud platforms
- Learning Docker multi-container deployments
- SSL certificate automation patterns
- Production nginx configurations

---

## ⚠️ Important Notes

- **DO NOT** run these scripts on the current codebase - paths have changed
- **DO NOT** commit API keys or credentials (already in .gitignore)
- **Reference only** - treat as documentation, not runnable code

---

**Current deployment**: See root `README.md` and `docker-compose.yml`
