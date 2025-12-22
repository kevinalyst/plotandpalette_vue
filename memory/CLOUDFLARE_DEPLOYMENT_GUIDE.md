# Cloudflare Deployment Guide - Plot & Palette

## Overview

This guide provides complete instructions for migrating Plot & Palette from the current Docker/Python backend to Cloudflare Pages + Workers + D1 + R2.

**Architecture:**
- Frontend: Vue app deployed to Cloudflare Pages
- API: Cloudflare Workers (Pages Functions) - ONLY public API surface
- Database: Cloudflare D1 (SQLite)
- Storage: Cloudflare R2 (images/assets)
- AI Workflows: n8n (private, triggered by Worker, NOT publicly exposed)

---

## Prerequisites

1. **Cloudflare Account** with Pages and Workers enabled
2. **Wrangler CLI** installed:
   ```bash
   npm install -g wrangler
   wrangler login
   ```
3. **Node.js** 18+ and npm
4. **n8n instance** (separate deployment, receives webhooks from Worker)

---

## Phase 1: Infrastructure Setup

### Step 1.1: Install Dependencies

```bash
cd apps/frontend
npm install @cloudflare/workers-types --save-dev
```

### Step 1.2: Create D1 Database

```bash
# Production database
wrangler d1 create plotpalette-db

# Copy the database_id from output and update wrangler.toml
# Output will be: database_id = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

# Development database
wrangler d1 create plotpalette-db-dev

# Copy the database_id for dev environment
```

**Update `wrangler.toml`:**
```toml
[[d1_databases]]
binding = "DB"
database_name = "plotpalette-db"
database_id = "YOUR_PROD_DATABASE_ID_HERE"

[[env.dev.d1_databases]]
binding = "DB"
database_name = "plotpalette-db-dev"
database_id = "YOUR_DEV_DATABASE_ID_HERE"
```

### Step 1.3: Run D1 Migrations

```bash
# Production
wrangler d1 migrations apply plotpalette-db

# Development
wrangler d1 migrations apply plotpalette-db-dev --env dev
```

### Step 1.4: Create R2 Buckets

```bash
# Production bucket
wrangler r2 bucket create plotpalette-assets-prod

# Development bucket
wrangler r2 bucket create plotpalette-assets-dev
```

### Step 1.5: Set Secrets

```bash
# Production secrets
wrangler secret put API_KEY
# Enter a strong API key (e.g., generate with: openssl rand -hex 32)

wrangler secret put N8N_SHARED_SECRET
# Enter the shared secret for n8n webhook authentication

wrangler secret put N8N_CALLBACK_SECRET
# Enter the secret for verifying n8n callbacks (HMAC)

# Development secrets (optional)
wrangler secret put API_KEY --env dev
wrangler secret put N8N_SHARED_SECRET --env dev
wrangler secret put N8N_CALLBACK_SECRET --env dev
```

---

## Phase 2: Code Structure

### Directory Structure

```
apps/frontend/
├── functions/              # Cloudflare Pages Functions (API endpoints)
│   ├── types/
│   │   └── env.d.ts       # Environment & type definitions
│   ├── lib/               # Shared utilities
│   │   ├── db.ts          # D1 database helpers
│   │   ├── r2.ts          # R2 storage helpers
│   │   ├── n8n.ts         # n8n webhook helpers
│   │   └── utils.ts       # General utilities
│   └── api/
│       ├── _middleware.ts # CORS, auth, error handling
│       ├── health.ts      # GET /api/health
│       ├── status.ts      # GET /api/status
│       ├── users/
│       │   ├── check.ts   # POST /api/users/check
│       │   └── index.ts   # POST /api/users
│       ├── sessions/
│       │   ├── index.ts   # POST /api/sessions
│       │   └── [session_id].ts  # GET /api/sessions/:id
│       ├── palettes/
│       │   ├── upload.ts  # POST /api/palettes/upload
│       │   └── [asset_id].ts    # GET /api/palettes/:id
│       ├── jobs/
│       │   ├── index.ts   # POST, GET /api/jobs
│       │   └── [job_id].ts      # GET /api/jobs/:id
│       ├── internal/
│       │   └── jobs/
│       │       └── [job_id]/
│       │           └── callback.ts  # POST (n8n callback)
│       ├── emotions.ts    # POST /api/emotions
│       ├── selections.ts  # POST /api/selections
│       ├── feedback.ts    # POST /api/feedback
│       ├── assets/
│       │   └── [asset_id].ts    # GET /api/assets/:id
│       └── proxy.ts       # GET /api/proxy
├── src/                   # Vue frontend source
├── dist/                  # Build output
└── package.json
```

---

## Phase 3: API Implementation Guide

### Authentication Flow

All protected endpoints require:
```
Header: X-API-Key: YOUR_API_KEY
```

### Job-Based Async Pattern

Heavy operations (ML, AI) use async jobs:

1. **Create Job**: `POST /api/jobs`
   ```json
   {
     "type": "PALETTE_ANALYSIS",
     "session_id": "xxx",
     "input_data": {...},
     "client_request_id": "uuid" // For idempotency
   }
   ```
   Response: `{job_id, status: "QUEUED"}`

2. **Poll Job Status**: `GET /api/jobs/{job_id}`
   ```json
   {
     "job_id": "xxx",
     "status": "RUNNING" | "SUCCEEDED" | "FAILED",
     "result_data": {...}, // When SUCCEEDED
     "error_message": "..." // When FAILED
   }
   ```

3. **Worker Triggers n8n**: Worker sends webhook to n8n with job details

4. **n8n Calls Back**: When complete, n8n calls `POST /api/internal/jobs/{job_id}/callback`

### Key Endpoints to Implement

#### Users & Sessions
- `POST /api/users/check` - Check if username exists
- `POST /api/users` - Create user with demographics
- `POST /api/sessions` - Create new session
- `GET /api/sessions/{session_id}` - Get full session data

#### Assets & Storage
- `POST /api/palettes/upload` - Upload image to R2
- `GET /api/assets/{asset_id}` - Serve asset from R2
- `GET /api/proxy?url=` - Proxy external images

#### Async Jobs
- `POST /api/jobs` - Create job (palette analysis, recommendations, story)
- `GET /api/jobs/{job_id}` - Get job status
- `GET /api/jobs?session_id=xxx` - List session jobs
- `POST /api/internal/jobs/{job_id}/callback` - n8n callback (HMAC verified)

#### Data Storage
- `POST /api/emotions` - Save emotion selection
- `POST /api/selections` - Save painting selection
- `POST /api/feedback` - Save feedback form

---

## Phase 4: Frontend Updates

### Update API Client (`apps/frontend/src/services/api.js`)

```javascript
// Update base API to use Cloudflare worker
const API_BASE = '/api'
const API_KEY = import.meta.env.VITE_API_KEY // Set in .env

class ApiService {
  async request(endpoint, options = {}) {
    const config = {
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY, // Add API key header
        ...options.headers,
      },
      ...options,
    }
    
    // ... rest of implementation
  }
  
  // Add job polling helper
  async pollJob(jobId, maxAttempts = 60, interval = 2000) {
    for (let i = 0; i < maxAttempts; i++) {
      const job = await this.request(`/jobs/${jobId}`)
      
      if (job.status === 'SUCCEEDED') {
        return job.result_data
      } else if (job.status === 'FAILED') {
        throw new Error(job.error_message || 'Job failed')
      }
      
      // Wait before next poll
      await new Promise(resolve => setTimeout(resolve, interval))
    }
    
    throw new Error('Job polling timeout')
  }
}
```

### Update Components for Async Jobs

Example for palette capture (in `GradientPalette.vue`):

```javascript
async capturePalette() {
  // 1. Create job
  const job = await ApiService.createJob({
    type: 'PALETTE_ANALYSIS',
    session_id: this.sessionId,
    input_data: {
      gifName: this.gifName,
      frameData: this.capturedFrame
    }
  })
  
  // 2. Poll for result
  showLoading.value = true
  loadingMessage.value = 'Analyzing your palette...'
  
  try {
    const result = await ApiService.pollJob(job.job_id)
    // Handle result...
  } catch (error) {
    // Handle error...
  } finally {
    showLoading.value = false
  }
}
```

---

## Phase 5: n8n Workflow Setup

### n8n Webhook Configuration

1. **Create Workflow** in n8n with Webhook trigger

2. **Webhook URL**: `https://your-n8n-instance.com/webhook/plotpalette`

3. **Authentication**: Verify `X-Shared-Secret` header matches `N8N_SHARED_SECRET`

4. **Workflow Steps**:
   - Receive webhook from Worker
   - Parse job type and input data
   - Execute appropriate AI/ML workflow
   - Call Worker callback endpoint with results

5. **Callback Request**:
   ```
   POST /api/internal/jobs/{job_id}/callback
   Headers:
     X-Signature: HMAC-SHA256(body, N8N_CALLBACK_SECRET)
   Body:
     {
       "status": "SUCCEEDED" | "FAILED",
       "result": {...},
       "error": "..."
     }
   ```

---

## Phase 6: Deployment

### Local Development

```bash
# Terminal 1: Run Pages Functions locally
cd apps/frontend
wrangler pages dev dist --binding DB=YOUR_DEV_DB_ID --binding ASSETS=YOUR_DEV_R2

# Terminal 2: Run Vue dev server
npm run dev
```

### Production Deployment

```bash
# Build frontend
cd apps/frontend
npm run build

# Deploy to Cloudflare Pages
wrangler pages deploy dist --project-name=plotpalette

# Or connect to GitHub for automatic deployments
```

---

## Phase 7: Environment Variables

### Required Environment Variables

**Cloudflare Dashboard** → Pages → Settings → Environment Variables:

```
VITE_API_KEY=your-api-key-here
```

**Worker Secrets** (already set in Phase 1):
- `API_KEY`
- `N8N_SHARED_SECRET`
- `N8N_CALLBACK_SECRET`

**wrangler.toml vars**:
- `ENVIRONMENT`
- `N8N_WEBHOOK_URL`
- `CORS_ORIGIN`

---

## Phase 8: Testing Checklist

- [ ] Health check: `GET /api/health`
- [ ] User registration: `POST /api/users`
- [ ] Session creation: `POST /api/sessions`
- [ ] Image upload to R2: `POST /api/palettes/upload`
- [ ] Job creation: `POST /api/jobs`
- [ ] Job polling: `GET /api/jobs/{job_id}`
- [ ] n8n webhook trigger (manual test)
- [ ] n8n callback (manual test with HMAC)
- [ ] Emotion save: `POST /api/emotions`
- [ ] Selection save: `POST /api/selections`
- [ ] Story generation job
- [ ] Feedback submission: `POST /api/feedback`
- [ ] Image proxy: `GET /api/proxy?url=...`

---

## Phase 9: Migration Strategy

### Zero-Downtime Migration

1. **Parallel Operation**:
   - Keep existing Python backend running
   - Deploy Cloudflare stack
   - Use feature flag to route traffic

2. **Gradual Migration**:
   - Week 1: 10% traffic to Cloudflare
   - Week 2: 50% traffic
   - Week 3: 100% traffic
   - Week 4: Decommission Python backend

3. **Data Migration**:
   - Export MySQL data
   - Transform to D1 schema
   - Import via D1 API or CSV

---

## Phase 10: Monitoring & Observability

### Cloudflare Analytics
- Enable Workers Analytics
- Set up error tracking
- Monitor D1 query performance
- Track R2 bandwidth usage

### Logging Strategy
```typescript
// In handlers
console.log('INFO:', { session_id, action, duration });
console.error('ERROR:', { error, context });
```

### Alerts
- Job failure rate > 5%
- API error rate > 1%
- D1 query time > 1s
- R2 upload failures

---

## Troubleshooting

### Common Issues

**Issue**: `Database not found`
```bash
# Verify database ID in wrangler.toml matches created database
wrangler d1 list
```

**Issue**: `R2 bucket not accessible`
```bash
# Verify bucket exists
wrangler r2 bucket list
```

**Issue**: `CORS errors`
- Check `CORS_ORIGIN` in wrangler.toml
- Verify middleware is applied to all routes

**Issue**: `Job stuck in QUEUED`
- Check n8n webhook URL is correct
- Verify n8n can reach Worker callback endpoint
- Check n8n logs for errors

---

## Cost Estimates

### Cloudflare Pricing (as of 2024)

**Free Tier Includes:**
- Pages: Unlimited requests
- Workers: 100,000 requests/day
- D1: 5GB storage, 5M reads/day, 100K writes/day
- R2: 10GB storage, 10M Class A requests

**Paid Tier (Workers Paid $5/month):**
- Workers: 10M requests
- D1: 25GB storage, 25M reads, 50M writes
- R2: Pay-as-you-go ($0.015/GB storage)

**Estimated Monthly Cost:**
- 100K users: ~$20-50/month
- 1M users: ~$100-200/month

---

## Security Considerations

1. **API Key Rotation**: Rotate API_KEY monthly
2. **Rate Limiting**: Implement per-IP and per-session limits
3. **HMAC Verification**: Always verify n8n callback signatures
4. **Input Validation**: Sanitize all user inputs
5. **SQL Injection**: Use parameterized queries (D1 handles this)
6. **XSS Prevention**: Escape outputs in frontend
7. **CORS**: Restrict to known origins only

---

## Support & Resources

- **Cloudflare Docs**: https://developers.cloudflare.com
- **D1 Documentation**: https://developers.cloudflare.com/d1/
- **R2 Documentation**: https://developers.cloudflare.com/r2/
- **Pages Functions**: https://developers.cloudflare.com/pages/functions/
- **n8n Documentation**: https://docs.n8n.io

---

## Next Steps

1. ✅ Review this guide
2. ✅ Complete Phase 1: Infrastructure Setup
3. ⏳ Implement core endpoints (health, users, sessions)
4. ⏳ Implement job system with n8n integration
5. ⏳ Update frontend to use new API
6. ⏳ Test end-to-end flow
7. ⏳ Deploy to production
8. ⏳ Monitor and optimize

**Questions?** Refer to the endpoint inventory table in the planning document for complete API specifications.
