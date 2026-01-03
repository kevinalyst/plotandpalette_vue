# 🎨 Plot & Palette

An interactive art-emotion-storytelling platform designed for high school teachers to explore the connection between colors, emotions, and artworks through AI-powered recommendations and narrative generation.

**Live Demo:** https://f48f6315.plotandpalette-vue-local.pages.dev

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

## 📊 API Endpoints (17 Total)

### User & Session
- `POST /api/store-username` - Create user + session
- `POST /api/users/check` - Verify username exists
- `GET /api/health` - Health check

### Uploads
- `POST /api/uploads/screenshot` - Upload palette screenshot to R2
- `POST /api/uploads/palette` - Upload custom palette image
- `GET /api/uploads/*` - Serve uploaded files

### Jobs (Async Processing)
- `POST /api/jobs` - Create job (palette analysis, recommendations, story)
- `GET /api/jobs/:job_id` - Get job status/result
- `GET /api/jobs?session_id=xxx` - List session jobs
- `POST /api/internal/jobs/:job_id/callback` - n8n callback (internal)

### Recommendations
- `POST /api/recommendations/compute` - Compute painting recommendations
- `GET /api/recommendations/:session_id` - Fetch saved recommendations

### Data Storage
- `POST /api/save-emotion` - Save emotion selection
- `POST /api/save-selection` - Save painting selections
- `POST /api/feedback` - Save user feedback

### Assets
- `GET /api/assets/**` - Serve static assets from R2

**Full Documentation:** See `memory/ENDPOINTS-DOCUMENTATION.md`

---

## 🗄️ Database Schema

**11 Tables:**
- `users` - User demographics (teachers)
- `sessions` - User sessions
- `jobs` - Async job queue
- `job_results` - Job outputs
- `palette_analysis` - Color analysis results
- `emotion_selections` - User emotion choices
- `painting_selections` - Selected artworks
- `art_information` - 155 paintings with color features
- `painting_recommendations` - AI recommendations
- `feedback` - User survey responses
- `assets` - R2 asset metadata

**Migrations:** 8 files in `apps/frontend/migrations/`

---

## 🎨 User Journey

1. **Homepage** → Register with invitation code (username + demographics)
2. **Gradient Palette** → Select from 20 animated color palettes
3. **Color Palette Page** → View extracted colors + emotion predictions (15 emotions with intensity)
4. **Gallery Page** → Browse 10 AI-recommended paintings, select 3 with character choice
5. **Story Page** → Read personalized story generated from selections
6. **Feedback** → Complete optional survey

---

## 🌐 Environment Variables

### Required Secrets (Cloudflare Dashboard)
```
API_KEY=<authentication-key>
N8N_SHARED_SECRET=<cloudflare-to-n8n-auth>
N8N_CALLBACK_SECRET=<n8n-callback-hmac-key>
```

### Required Variables (.dev.vars for local)
```
N8N_WEBHOOK_URL=<n8n-webhook-endpoint>
ENVIRONMENT=development
CORS_ORIGIN=*
```

---

## 📈 Production Stats

- **Frontend Bundle:** ~130 KiB (gzipped)
- **API Endpoints:** 17 serverless functions
- **Database Tables:** 11 tables, 8 migrations applied
- **Artwork Database:** 155 Chinese Contemporary Art paintings
- **Storage:** Cloudflare R2 (`plotpalette-assets-prod`)
- **Database:** Cloudflare D1 (`plotandplate-db`)

---

## 🧪 Testing

```bash
cd apps/frontend

# Run development server
npm run serve

# Build for production
npm run build

# Test API locally with Wrangler
npx wrangler pages dev dist --local

# Validate migrations
wrangler d1 migrations list plotandplate-db
```

---

## 📚 Documentation

Complete project documentation in the `memory/` folder (21 files):

**Architecture & Setup:**
- `CLOUDFLARE_DEPLOYMENT_GUIDE.md` - Full deployment instructions
- `PROJECT_PROGRESS_SUMMARY.md` - Feature changelog

**Features:**
- `STORY_GENERATION_JOB_FLOW.md` - Story generation pipeline
- `N8N_PAINTING_RECOMMENDATIONS.md` - Recommendation system
- `SETUP_ART_DATABASE.md` - Artwork database setup

**Bug Fixes:**
- `STORY_GENERATION_UNDEFINED_FIX.md`
- `GALLERY_PAGE_FIX.md`
- `N8N_401_FIX.md`

**Recent Updates:**
- `UI_IMPROVEMENTS_DEC_2025.md` - Select buttons, navigation
- `CODE_CLEANUP_JAN_2026.md` - Archival changelog

---

## 🗃️ Archive

The `archive/` folder contains obsolete code from the old architecture:
- **python-backend/** - Old Flask/Python API (replaced by Cloudflare Functions)
- **docker/** - Docker/nginx infrastructure (replaced by serverless)
- **setup-scripts/** - One-time data migration scripts
- **prototypes/** - Early HTML prototypes

**All archived code is preserved for reference but not actively maintained.**

---

## 🔄 Migration History

**December 2025:** Successfully migrated from Docker/Python/MySQL to Cloudflare Pages/Workers/D1/R2
- ✅ All ML/AI processing moved to n8n workflows
- ✅ Database migrated from MySQL to Cloudflare D1  
- ✅ Images moved to Cloudflare R2
- ✅ API endpoints migrated to Cloudflare Functions
- ✅ Zero-downtime migration completed

**January 2026:** Code cleanup and archival
- ✅ Archived ~70MB of obsolete Python backend
- ✅ Archived Docker infrastructure
- ✅ Clean, production-ready codebase

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
