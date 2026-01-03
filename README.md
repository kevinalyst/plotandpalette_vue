# 🎨 Plot & Palette

An interactive art-emotion-storytelling platform designed for high school teachers to explore the connection between colors, emotions, and artworks through AI-powered recommendations and narrative generation.

**Live Demo:** https://plotandpalette.uk/

---

## 🏗️ Modern Architecture (Cloudflare Stack)

```
┌─────────────────────────────────────────────────────┐
│     Vue.js Frontend (Cloudflare Pages)              │
│   - Color palette selection                         │
│   - Emotion analysis display                        │
│   - Painting gallery                                │
│   - Story presentation                              │
└─────────────┬───────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────┐
│   Cloudflare Pages Functions (Serverless API)      │
│   - 17 API endpoints                                │
│   - Job creation & management                      │
│   - Database operations (D1)                       │
│   - Asset serving (R2)                             │
└─────────────┬───────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────┐
│         n8n Workflows (External AI/ML)              │
│   - Palette emotion analysis                       │
│   - Painting recommendations                       │
│   - Story generation                               │
│   - HMAC-verified callbacks                        │
└─────────────────────────────────────────────────────┘
```

**Data Storage:**
- **Cloudflare D1** (SQLite) - User data, sessions, jobs, results
- **Cloudflare R2** - Images, screenshots, artwork (155 paintings)

---

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Wrangler CLI: `npm install -g wrangler`
- Cloudflare account (free tier works)

### Local Development

```bash
# 1. Clone repository
git clone https://github.com/kevinalyst/plotandpalette_vue.git
cd plotandpalette_vue/apps/frontend

# 2. Install dependencies
npm install

# 3. Set up environment variables
cp .dev.vars.example .dev.vars
# Edit .dev.vars with your API keys

# 4. Run development server
npm run serve

# 5. In another terminal, run Cloudflare Functions locally
npx wrangler pages dev dist --local
```

**Access:** http://localhost:8080

---

## 📦 Build & Deploy

### Build for Production

```bash
cd apps/frontend
npm run build
```

### Deploy to Cloudflare Pages

```bash
cd apps/frontend
npx wrangler pages deploy dist --project-name=plotandpalette-vue-local
```

### Apply Database Migrations

```bash
# Production database
wrangler d1 migrations apply plotandplate-db --remote

# Development database
wrangler d1 migrations apply plotandplate-db-dev --local
```

---

## 🗂️ Project Structure

```
plotandpalette_vue/
├── apps/frontend/              # Main application
│   ├── src/                    # Vue.js source code
│   │   ├── views/              # Page components
│   │   ├── components/         # Reusable components
│   │   ├── locales/            # i18n translations (EN/ZH)
│   │   ├── services/           # API client
│   │   └── router/             # Vue Router config
│   │
│   ├── functions/              # Cloudflare Pages Functions (API)
│   │   ├── api/                # API endpoints
│   │   ├── lib/                # Shared utilities
│   │   └── types/              # TypeScript definitions
│   │
│   ├── migrations/             # D1 database migrations (8 files)
│   ├── public/                 # Static assets
│   ├── palette GIF/            # Color palette animations
│   └── wrangler.toml           # Cloudflare configuration
│
├── data/
│   └── Chinese_Contemporary_Art/  # 155 artwork files + metadata
│
├── memory/                     # Project documentation (21 files)
│   ├── PROJECT_PROGRESS_SUMMARY.md
│   ├── CLOUDFLARE_DEPLOYMENT_GUIDE.md
│   ├── ENDPOINTS-DOCUMENTATION.md
│   └── ...
│
├── archive/                    # Archived code (old Python backend, Docker, etc.)
├── logs/                       # Runtime logs
└── uploads/                    # Runtime uploads
```

---

## 🎯 Key Features

1. **Color Palette Selection** - 20 animated gradient palettes to choose from
2. **Emotion Analysis** - ML-powered emotion intensity prediction (15 emotions)
3. **Smart Recommendations** - AI-curated artwork selection (155 Chinese Contemporary Art pieces)
4. **Story Generation** - Personalized narratives based on selected paintings and character
5. **Bilingual Support** - Full English/Chinese (中文) interface

---

## 🔧 Technology Stack

### Frontend
- **Framework:** Vue.js 3 (Composition API)
- **Build Tool:** Webpack
- **Styling:** Scoped CSS
- **i18n:** vue-i18n (English/Chinese)
- **Hosting:** Cloudflare Pages

### Backend (Serverless)
- **Functions:** Cloudflare Workers (TypeScript)
- **Database:** Cloudflare D1 (SQLite)
- **Storage:** Cloudflare R2
- **AI/ML:** n8n workflows (external)

### Infrastructure
- **DNS/CDN:** Cloudflare
- **Deployments:** Wrangler CLI
- **Version Control:** Git/GitHub

---

## 📝 License

This project is for academic research at Newcastle University (Ethics Approval No. 54009/2023).

---

## 🤝 Contributing

This is a research project. For questions or collaboration inquiries, see the team page in the application or check the documentation in `memory/`.

---

**Last Updated:** January 3, 2026  
**Architecture:** Cloudflare Pages (Serverless)  
**Status:** ✅ Production Ready
