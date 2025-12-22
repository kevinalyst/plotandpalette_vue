# Plot & Palette API Endpoints Documentation

This document provides a comprehensive overview of all API endpoints in the Plot & Palette Vue frontend application, including their types, data formats, and integration with n8n webhooks.

---

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [User & Session Management](#user--session-management)
4. [Palette & Emotion Endpoints](#palette--emotion-endpoints)
5. [Job System (n8n Integration)](#job-system-n8n-integration)
6. [Asset Serving](#asset-serving)
7. [n8n Webhook Integration Flow](#n8n-webhook-integration-flow)
8. [Data Models](#data-models)

---

## Overview

The Plot & Palette application uses:
- **Frontend**: Vue.js application (apps/frontend/src/)
- **API Service**: Centralized API client (apps/frontend/src/services/api.js)
- **Backend**: Cloudflare Pages Functions (apps/frontend/functions/api/)
- **Storage**: Cloudflare D1 (SQLite) + R2 (Object Storage)
- **External Processing**: n8n workflows for ML/AI tasks

**Base URL**: `/api`

**Standard Response Format**:
```json
{
  "success": true,
  "data": { /* response data */ },
  "message": "Optional message"
}
```

**Error Response Format**:
```json
{
  "success": false,
  "error": "Error message",
  "message": "Optional details"
}
```

---

## Authentication

All API requests include:
- **Header**: `X-API-Key: <API_KEY>`
- **Value**: Hardcoded in api.js (development) or from environment (production)

```javascript
headers: {
  'Content-Type': 'application/json',
  'X-API-Key': API_KEY
}
```

---

## User & Session Management

### 1. POST `/api/store-username`

**Purpose**: Create new user and session (backward compatibility endpoint)

**Implemented in**: `apps/frontend/functions/api/store-username.ts`

**Called from**: HomePage.vue → `submitUserInformation()`

**Request Body**:
```json
{
  "name": "kevin123",               // or "username"
  "age": "25-34",
  "gender": "man",
  "fieldOfStudy": "computer-science",
  "frequency": "weekly"
}
```

**Response**:
```json
{
  "success": true,
  "sessionId": "uuid-v4",
  "username": "kevin123",
  "message": "User created with new session"
}
```

**Behavior**:
- Checks if user exists in D1
- Creates user if new
- Always creates a new session
- Returns session ID to track user journey

---

### 2. POST `/api/users/check`

**Purpose**: Check if username exists in database

**Implemented in**: `apps/frontend/functions/api/users/check.ts`

**Called from**: HomePage.vue → `startJourney()`

**Request Body**:
```json
{
  "username": "kevin123"
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "exists": true,
    "username": "kevin123"
  }
}
```

**Use Case**: 
- Returning users: Check localStorage username → verify in DB → skip registration form
- New users: Show registration form

---

### 3. GET `/api/health`

**Purpose**: Health check endpoint

**Implemented in**: `apps/frontend/functions/api/health.ts`

**Called from**: HomePage.vue → `mounted()` lifecycle

**Response**:
```json
{
  "success": true,
  "message": "API is healthy",
  "timestamp": "2025-12-20T10:00:00.000Z"
}
```

---

## Palette & Emotion Endpoints

### 4. POST `/api/emotions`

**Purpose**: Save emotion selection and palette analysis data

**Implemented in**: `apps/frontend/functions/api/emotions.ts`

**Called from**: ColorPalettePage.vue (expected)

**Request Body**:
```json
{
  "session_id": "uuid-v4",
  "selected_emotion": "joy",
  "probability": 0.87,
  "palette_data": {
    "gif_name": "1.gif",
    "colour_data": ["#FF5733", "#33FF57", "#3357FF"],
    "raw_colors": [[255, 87, 51], [51, 255, 87], [51, 87, 255]],
    "emotion_scores": {
      "joy": 0.87,
      "sadness": 0.05,
      "anger": 0.03
    }
  }
}
```

**Response**:
```json
{
  "success": true,
  "message": "Emotion data saved successfully",
  "session_id": "uuid-v4"
}
```

**Database Actions**:
- Saves to `emotion_selections` table
- Saves to `palette_analyses` table

---

### 5. POST `/api/selections`

**Purpose**: Save painting selections

**Implemented in**: `apps/frontend/functions/api/selections.ts`

**Called from**: GalleryPage.vue (expected)

**Request Body**:
```json
{
  "session_id": "uuid-v4",
  "selected_paintings": [
    {
      "painting_id": "123",
      "title": "Starry Night",
      "artist": "Vincent van Gogh",
      "url": "https://..."
    },
    {
      "painting_id": "456",
      "title": "The Scream",
      "artist": "Edvard Munch",
      "url": "https://..."
    }
  ],
  "story_character": "explorer",
  "nickname": "kevin"
}
```

**Response**:
```json
{
  "success": true,
  "message": "Selection saved successfully",
  "session_id": "uuid-v4"
}
```

---

### 6. POST `/api/save-emotion`

**Purpose**: Save user's emotion selection (backward compatibility endpoint)

**Implemented in**: `apps/frontend/functions/api/save-emotion.ts`

**Called from**: ColorPalettePage.vue → `proceedToGallery()`

**Request Body**:
```json
{
  "emotion": "happiness",
  "intensity": "high",
  "sessionId": "uuid-v4"
}
```

**Response**:
```json
{
  "success": true,
  "message": "Emotion selection saved successfully",
  "sessionId": "uuid-v4",
  "selectedEmotion": {
    "emotion": "happiness",
    "intensity": "high"
  }
}
```

**Database Actions**:
- Saves to `emotion_selections` table with intensity level ("low", "medium", or "high")

**Validation**:
- `intensity` must be one of: "low", "medium", "high"

**Note**: This endpoint provides the same functionality as `/api/emotions` but matches the path expected by the legacy frontend `api.js` client.

---

### 7. POST `/api/save-selection`

**Purpose**: Save user's painting selections (backward compatibility endpoint)

**Implemented in**: `apps/frontend/functions/api/save-selection.ts`

**Called from**: GalleryPage.vue (expected)

**Request Body**:
```json
{
  "selectedPaintings": [
    {
      "url": "https://...",
      "title": "Starry Night",
      "artist": "Vincent van Gogh"
    },
    {
      "url": "https://...",
      "title": "The Scream",
      "artist": "Edvard Munch"
    },
    {
      "url": "https://...",
      "title": "The Kiss",
      "artist": "Gustav Klimt"
    }
  ],
  "character": "explorer",
  "nickname": "kevin",
  "emotion": "happiness",
  "intensity": "high",
  "sessionId": "uuid-v4"
}
```

**Response**:
```json
{
  "success": true,
  "message": "Selection saved successfully",
  "sessionId": "uuid-v4",
  "selectedPaintings": [...],
  "character": "explorer",
  "nickname": "kevin",
  "emotion": "happiness",
  "intensity": "high"
}
```

**Database Actions**:
- Saves to `painting_selections` table

**Note**: This endpoint provides the same functionality as `/api/selections` but matches the path expected by the legacy frontend `api.js` client. Requires exactly 3 paintings.

---

### 8. POST `/api/feedback`

**Purpose**: Save user feedback survey responses

**Implemented in**: `apps/frontend/functions/api/feedback.ts`

**Called from**: FeedbackPage.vue

**Request Body**:
```json
{
  "session_id": "uuid-v4",
  "q1": "answer to question 1",
  "q2": 5,
  "q3": "answer to question 3",
  "q4": 4,
  "q5": "answer to question 5",
  "q6": 3,
  "q7": "answer to question 7",
  "q8": 5,
  "q9": "answer to question 9",
  "q10": 4,
  "q11": "answer to question 11",
  "q12": 5,
  "q13": "answer to question 13",
  "q14": 3,
  "q15": "answer to question 15",
  "prolific_pid": "abc123",
  "prolific_study_id": "study456",
  "prolific_session_id": "session789"
}
```

**Response**:
```json
{
  "success": true,
  "message": "Feedback saved successfully",
  "session_id": "uuid-v4"
}
```

---

## Job System (n8n Integration)

---

## Upload Endpoints

### 9. POST `/api/uploads/screenshot`

**Purpose**: Upload screenshot to R2 for palette analysis

**Implemented in**: `apps/frontend/functions/api/uploads/screenshot.ts`

**Called from**: GradientPalette.vue → `capturePalette()`

**Request Body**:
```json
{
  "screenshot": "data:image/png;base64,iVBORw0KGgo...",
  "session_id": "uuid-v4",
  "palette_no": 5
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "key": "screenshots/screenshot-1234567890-uuid.png",
    "url": "/api/assets/screenshots/screenshot-1234567890-uuid.png",
    "size": 245678
  }
}
```

**Backend Actions**:
1. Decodes base64 screenshot
2. Uploads to R2 bucket under `screenshots/` prefix
3. Returns R2 key for job creation

---

### 10. POST `/api/uploads/palette`

**Purpose**: Upload user's custom palette image to R2

**Implemented in**: `apps/frontend/functions/api/uploads/palette.ts`

**Called from**: GradientPalette.vue → `handleFileUpload()` (upload tile)

**Request Body**: FormData
```
FormData {
  image: File (PNG/JPEG/WebP, max 10MB)
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "key": "palettes/user-upload-1234567890-uuid.png",
    "url": "/api/assets/palettes/user-upload-1234567890-uuid.png",
    "filename": "my-palette.png",
    "size": 156789,
    "contentType": "image/png",
    "message": "Palette image uploaded successfully"
  }
}
```

**Validation**:
- Allowed types: PNG, JPEG, WebP
- Maximum size: 10MB
- Generates unique filename

**Use Case**: Allows users to upload their own palette images for color analysis instead of using the provided GIFs.

---

## Job System (n8n Integration)

### 11. POST `/api/jobs`

**Purpose**: Create a new job for external processing (triggers n8n workflow)

**Implemented in**: `apps/frontend/functions/api/jobs/index.ts`

**Called from**: Frontend views (ColorPalettePage, GalleryPage, StoryPage)

**Request Body**:
```json
{
  "type": "STORY_GENERATION",
  "session_id": "uuid-v4",
  "input_data": {
    "paintings": [
      {
        "url": "https://...",
        "title": "Starry Night",
        "artist": "Vincent van Gogh"
      }
    ],
      "character": "explorer",
      "nickname": "kevin",
      "emotion": "joy",
      "intensity": "high"
  },
  "client_request_id": "optional-client-id"
}
```

**Job Types**:
- `PALETTE_ANALYSIS` - Analyze color palette for emotions
- `PAINTING_RECOMMENDATION` - Get painting recommendations
- `STORY_GENERATION` - Generate personalized story

**Response**:
```json
{
  "success": true,
  "data": {
    "job_id": "job-uuid-v4",
    "status": "QUEUED"
  }
}
```

**Backend Actions**:
1. Creates job in D1 database with status `QUEUED`
2. Triggers n8n webhook with job details
3. Returns job_id to frontend for polling

---

### 12. GET `/api/jobs?session_id=xxx`

**Purpose**: Get all jobs for a session

**Implemented in**: `apps/frontend/functions/api/jobs/index.ts`

**Query Parameters**:
- `session_id` (required): Session UUID

**Response**:
```json
{
  "success": true,
  "data": {
    "jobs": [
      {
        "job_id": "job-uuid-1",
        "type": "PALETTE_ANALYSIS",
        "status": "COMPLETED",
        "created_at": "2025-12-20T10:00:00.000Z",
        "completed_at": "2025-12-20T10:00:05.000Z"
      },
      {
        "job_id": "job-uuid-2",
        "type": "STORY_GENERATION",
        "status": "RUNNING",
        "created_at": "2025-12-20T10:01:00.000Z"
      }
    ]
  }
}
```

---

### 13. GET `/api/jobs/:job_id`

**Purpose**: Get job status and result

**Implemented in**: `apps/frontend/functions/api/jobs/[job_id].ts`

**Response**:
```json
{
  "success": true,
  "data": {
    "job_id": "job-uuid-v4",
    "type": "STORY_GENERATION",
    "status": "COMPLETED",
    "input_data": "{ /* original input */ }",
    "result_data": {
      "story": "Once upon a time...",
      "metadata": {}
    },
    "r2_result_key": "results/job-uuid-v4.json",
    "created_at": "2025-12-20T10:00:00.000Z",
    "completed_at": "2025-12-20T10:00:15.000Z"
  }
}
```

**Status Values**:
- `QUEUED` - Job created, waiting for processing
- `RUNNING` - Job is being processed by n8n
- `COMPLETED` - Job finished successfully
- `FAILED` - Job failed with error

---

### 14. POST `/api/internal/jobs/:job_id/callback` (Internal - n8n only)

**Purpose**: Receive completion callback from n8n workflow

**Implemented in**: `apps/frontend/functions/api/internal/jobs/[job_id]/callback.ts`

**Security**: HMAC signature verification via `X-N8N-Signature` header

**Request Body** (from n8n):
```json
{
  "job_id": "job-uuid-v4",
  "success": true,
  "result_data": {
    "story": "Generated story text...",
    "metadata": {}
  },
  "r2_result_key": "results/job-uuid-v4.json",
  "error_message": null
}
```

**Response**:
```json
{
  "success": true,
  "message": "Callback processed successfully",
  "job_id": "job-uuid-v4",
  "status": "COMPLETED"
}
```

**Backend Actions**:
1. Verifies HMAC signature from n8n
2. Updates job status in D1 to `COMPLETED` or `FAILED`
3. Saves result data to D1/R2
4. Records completion timestamp

---

## Asset Serving

### 15. GET `/api/assets/**`

**Purpose**: Serve static assets from R2 bucket

**Implemented in**: `apps/frontend/functions/api/assets/[[path]].ts`

**Called from**: 
- gifPreloader.js → preloads palette GIFs
- GradientPalette.vue → loads palette GIFs and user uploads
- ColorPalettePage.vue → displays captured screenshots

**Example Requests**:
```
GET /api/assets/palettes/1.gif
GET /api/assets/palettes/2.gif
GET /api/assets/screenshots/screenshot-123.png
GET /api/assets/palettes/user-upload-456.png
```

**Response**: Binary file with appropriate headers:
```
Content-Type: image/gif | image/png | image/jpeg
Cache-Control: public, max-age=31536000
Access-Control-Allow-Origin: *
```

**Supported Paths**:
- `palettes/*.gif` - Built-in palette GIF files
- `palettes/user-upload-*.{png,jpg,webp}` - User-uploaded palette images
- `screenshots/*.png` - Captured palette screenshots

**Backend Actions**:
1. Extracts full path from URL
2. Fetches file from R2 bucket (`ASSET_BUCKET`)
3. Returns binary content with appropriate cache and CORS headers

---

## n8n Webhook Integration Flow

### Complete Integration Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│ 1. Vue Frontend                                                      │
│    - User completes palette selection                                │
│    - User selects paintings                                          │
│    - User requests story generation                                  │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         │ POST /api/jobs
                         │ {
                         │   "type": "STORY_GENERATION",
                         │   "session_id": "uuid",
                         │   "input_data": { paintings, character, etc }
                         │ }
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 2. Cloudflare Function: jobs/index.ts                                │
│    - Creates job record in D1 database                               │
│    - Status: QUEUED                                                  │
│    - Generates unique job_id                                         │
│    - Prepares n8n webhook payload                                    │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         │ Triggers n8n webhook
                         │
                         │ POST {N8N_WEBHOOK_URL}
                         │ Headers:
                         │   X-Shared-Secret: {N8N_SHARED_SECRET}
                         │ Body:
                         │ {
                         │   "job_id": "job-uuid",
                         │   "session_id": "session-uuid",
                         │   "job_type": "STORY_GENERATION",
                         │   "input_data": { /* user data */ },
                         │   "callback_url": "https://.../api/internal/jobs/{job_id}/callback"
                         │ }
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 3. n8n Workflow (External Processing)                                │
│    - Receives webhook trigger                                        │
│    - Validates X-Shared-Secret                                       │
│    - Routes to appropriate workflow:                                 │
│      * PALETTE_ANALYSIS → Emotion Prediction API                     │
│      * PAINTING_RECOMMENDATION → Recommendation Service              │
│      * STORY_GENERATION → Story Generation API                       │
│    - Processes data (ML/AI operations)                               │
│    - Stores large results in R2 if needed                            │
│    - Prepares callback payload                                       │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         │ Calls callback URL
                         │
                         │ POST /api/internal/jobs/{job_id}/callback
                         │ Headers:
                         │   X-N8N-Signature: HMAC-SHA256(body, N8N_CALLBACK_SECRET)
                         │ Body:
                         │ {
                         │   "job_id": "job-uuid",
                         │   "success": true,
                         │   "result_data": { /* processed results */ },
                         │   "r2_result_key": "results/job-uuid.json"
                         │ }
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 4. Cloudflare Function: callback.ts                                  │
│    - Verifies HMAC signature                                         │
│    - Updates job status: COMPLETED or FAILED                         │
│    - Saves result_data to D1                                         │
│    - Records r2_result_key for large results                         │
│    - Records completion timestamp                                    │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         │ Job complete!
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 5. Vue Frontend (Polling)                                            │
│    - Polls GET /api/jobs/{job_id} every 2 seconds                   │
│    - Checks status: QUEUED → RUNNING → COMPLETED                    │
│    - Retrieves result_data when status = COMPLETED                  │
│    - Displays result to user (story, recommendations, etc)           │
└─────────────────────────────────────────────────────────────────────┘
```

### n8n Webhook Configuration

**Environment Variables Required**:

| Variable | Purpose | Location |
|----------|---------|----------|
| `N8N_WEBHOOK_URL` | n8n webhook trigger URL | Cloudflare Pages settings |
| `N8N_SHARED_SECRET` | Authenticates Cloudflare → n8n requests | Both sides |
| `N8N_CALLBACK_SECRET` | HMAC key for n8n → Cloudflare callbacks | Both sides |

**Security Features**:
1. **Outbound (CF → n8n)**: Shared secret in header
2. **Inbound (n8n → CF)**: HMAC-SHA256 signature verification
3. **Internal endpoint**: `/api/internal/jobs/...` not exposed to frontend

---

### n8n Callback Payload Formats

#### PALETTE_ANALYSIS Job Callback

n8n must return emotion intensity levels (not probabilities):

```json
{
  "success": true,
  "result_data": {
    "filename": "screenshot-abc123.png",
    "rawColors": {
      "#8b54b5": 0.1027,
      "#ffc0cb": 0.2515,
      "#3a5f8a": 0.1893
    },
    "colourData": {
      "purple": 0.10,
      "pink": 0.25,
      "blue": 0.19
    },
    "emotionPrediction": {
      "emotion": "happiness",
      "all_intensities": {
        "happiness": "high",
        "love": "medium",
        "optimism": "medium",
        "trust": "low",
        "anticipation": "low",
        "surprise": "low",
        "fear": "low",
        "sadness": "low",
        "anger": "low",
        "disgust": "low",
        "gratitude": "medium",
        "humility": "low",
        "arrogance": "low",
        "pessimism": "low",
        "disagreeableness": "low"
      }
    }
  }
}
```

**Important Changes from Previous Version:**
- ❌ **REMOVED**: `all_probabilities` (old probability-based system)
- ✅ **NEW**: `all_intensities` with values: "low", "medium", "high"
- Frontend displays 3-star rating system based on intensity
- Database stores intensity TEXT instead of probability REAL

---

### n8n Integration Helper Functions

**Location**: `apps/frontend/functions/lib/n8n.ts`

**1. triggerN8nWorkflow()**
```typescript
async function triggerN8nWorkflow(env: Env, job: Job): Promise<void>
```
- Sends POST request to n8n webhook URL
- Includes job details and callback URL
- Handles errors gracefully

**2. verifyN8nCallback()**
```typescript
async function verifyN8nCallback(
  env: Env, 
  body: string, 
  signature: string
): Promise<boolean>
```
- Verifies HMAC-SHA256 signature
- Prevents unauthorized callbacks
- Returns true if valid

**3. parseN8nCallback()**
```typescript
function parseN8nCallback(body: string): N8nCallbackPayload
```
- Parses callback JSON
- Validates required fields
- Returns typed payload

---

## Data Models

### User
```typescript
{
  username: string;          // Primary key, min 6 chars, letters + numbers
  age: string;              // Range: "18-24", "25-34", etc.
  gender: string;           // "man", "woman", "non-binary", "prefer-not-to-say"
  field_of_study: string;   // Study/profession category
  frequency: string;        // Art engagement frequency
  created_at: string;       // ISO timestamp
}
```

### Session
```typescript
{
  session_id: string;       // UUID v4, primary key
  username: string;         // Foreign key to users
  created_at: string;       // ISO timestamp
  completed_at?: string;    // When user finishes journey
}
```

### Job
```typescript
{
  job_id: string;           // UUID v4, primary key
  session_id: string;       // Foreign key to sessions
  type: JobType;            // "PALETTE_ANALYSIS" | "PAINTING_RECOMMENDATION" | "STORY_GENERATION"
  status: JobStatus;        // "QUEUED" | "RUNNING" | "SUCCEEDED" | "FAILED"
  client_request_id?: string; // Optional client tracking ID
  input_data: string;       // JSON string of input
  result_data?: string;     // JSON string of result (small results)
  r2_result_key?: string;   // R2 path for large results
  error_message?: string;   // Error details if failed
  created_at: string;       // ISO timestamp
  started_at?: string;      // When processing started
  completed_at?: string;    // When processing finished
}
```

### Emotion Selection
```typescript
{
  id: number;               // Auto-increment
  session_id: string;       // Foreign key to sessions
  selected_emotion: string; // E.g., "joy", "sadness", "anger"
  intensity: string;        // Intensity level: "low", "medium", or "high"
  probability: number;      // DEPRECATED - kept for backward compatibility
  created_at: string;       // ISO timestamp
}
```

### Palette Analysis
```typescript
{
  id: number;               // Auto-increment
  session_id: string;       // Foreign key to sessions
  gif_name: string;         // E.g., "1.gif"
  colour_data: string;      // JSON array of hex colors
  raw_colors: string;       // JSON array of RGB arrays
  emotion_scores: string;   // JSON object of emotion probabilities
  created_at: string;       // ISO timestamp
}
```

### Painting Selection
```typescript
{
  id: number;               // Auto-increment
  session_id: string;       // Foreign key to sessions
  selected_paintings: string; // JSON array of painting objects
  story_character: string;  // Character choice for story
  nickname: string;         // User's nickname for story
  created_at: string;       // ISO timestamp
}
```

### Feedback
```typescript
{
  id: number;               // Auto-increment
  session_id: string;       // Foreign key to sessions
  q1: string;               // Answer to question 1
  q2: number;               // Rating 1-5
  q3: string;               // ...
  q4: number;
  q5: string;
  q6: number;
  q7: string;
  q8: number;
  q9: string;
  q10: number;
  q11: string;
  q12: number;
  q13: string;
  q14: number;
  q15: string;
  prolific_pid?: string;    // Prolific participant ID
  prolific_study_id?: string; // Prolific study ID
  prolific_session_id?: string; // Prolific session ID
  created_at: string;       // ISO timestamp
}
```

---

## Legacy Endpoints Status

### ✅ Now Implemented:
- `POST /api/save-emotion` - Save emotion selection (backward compatibility)
- `POST /api/save-selection` - Save painting selection (backward compatibility)
- `POST /api/uploads/palette` - Upload user palette image to R2

### 🔄 Migrated to Jobs System:
- `POST /api/get-recommendations` → Use `POST /api/jobs` with type `PAINTING_RECOMMENDATION`
- `POST /api/get-recommendations-from-colors` → Use `POST /api/jobs` with type `PAINTING_RECOMMENDATION`
- `POST /api/generate-story` → Use `POST /api/jobs` with type `STORY_GENERATION`

### ❌ Not Implemented (Not Required):
- `POST /api/save-palette` - Replaced by `/api/uploads/palette` and `/api/uploads/screenshot`
- `GET /api/palette/:filename` - Not needed with R2 direct serving
- `GET /api/recent-palettes` - Not required for MVP
- `GET /api/session-palette/:sessionId` - Data available through jobs system
- `GET /api/selection-history` - Not required for MVP
- `GET /api/status` - Use `/api/health` instead

---

## API Client Usage Examples

### Example 1: User Registration Flow
```javascript
// HomePage.vue - submitUserInformation()
const response = await ApiService.request('/store-username', {
  method: 'POST',
  body: JSON.stringify({
    name: 'kevin123',
    age: '25-34',
    gender: 'man',
    fieldOfStudy: 'computer-science',
    frequency: 'weekly'
  })
});

const username = response.data?.username || response.username;
localStorage.setItem('username', username);
```

### Example 2: Returning User Check
```javascript
// HomePage.vue - startJourney()
const existingUsername = localStorage.getItem('username');

if (existingUsername) {
  const response = await ApiService.request('/users/check', {
    method: 'POST',
    body: JSON.stringify({
      username: existingUsername
    })
  });
  
  const exists = response.data?.exists || response.exists;
  
  if (exists) {
    // User verified, proceed to app
  } else {
    // Show registration form
  }
}
```

### Example 3: Job Creation and Polling
```javascript
// Create job
const createResponse = await ApiService.request('/jobs', {
  method: 'POST',
  body: JSON.stringify({
    type: 'STORY_GENERATION',
    session_id: sessionId,
    input_data: {
      paintings: selectedPaintings,
      character: 'explorer',
      nickname: 'kevin'
    }
  })
});

const jobId = createResponse.data.job_id;

// Poll for completion
const pollInterval = setInterval(async () => {
  const statusResponse = await ApiService.request(`/jobs/${jobId}`);
  
  if (statusResponse.data.status === 'COMPLETED') {
    clearInterval(pollInterval);
    const story = statusResponse.data.result_data.story;
    // Display story to user
  } else if (statusResponse.data.status === 'FAILED') {
    clearInterval(pollInterval);
    // Handle error
  }
}, 2000);
```

---

## Summary

### Currently Implemented Endpoints (Cloudflare Functions)

| Endpoint | Method | Purpose | Status |
|----------|--------|---------|--------|
| `/api/health` | GET | Health check | ✅ Implemented |
| `/api/store-username` | POST | User + session creation | ✅ Implemented |
| `/api/users/check` | POST | Check user exists | ✅ Implemented |
| `/api/emotions` | POST | Save emotion data | ✅ Implemented |
| `/api/selections` | POST | Save painting selections | ✅ Implemented |
| `/api/save-emotion` | POST | Save emotion (compat) | ✅ Implemented |
| `/api/save-selection` | POST | Save selection (compat) | ✅ Implemented |
| `/api/feedback` | POST | Save feedback | ✅ Implemented |
| `/api/uploads/screenshot` | POST | Upload screenshot to R2 | ✅ Implemented |
| `/api/uploads/palette` | POST | Upload user palette to R2 | ✅ Implemented |
| `/api/jobs` | POST | Create job | ✅ Implemented |
| `/api/jobs` | GET | List jobs | ✅ Implemented |
| `/api/jobs/:job_id` | GET | Get job status | ✅ Implemented |
| `/api/internal/jobs/:job_id/callback` | POST | n8n callback | ✅ Implemented |
| `/api/assets/**` | GET | Serve R2 assets | ✅ Implemented |

### n8n Integration

✅ **Fully Integrated**:
- Job creation triggers n8n webhooks
- HMAC signature verification for callbacks
- Async processing with status polling
- Result storage in D1/R2

---

## References

- **Frontend API Client**: `apps/frontend/src/services/api.js`
- **Cloudflare Functions**: `apps/frontend/functions/api/`
- **n8n Helpers**: `apps/frontend/functions/lib/n8n.ts`
- **Database Helpers**: `apps/frontend/functions/lib/db.ts`
- **Type Definitions**: `apps/frontend/functions/types/env.d.ts`
- **Database Schema**: `migrations/0001_initial_schema.sql`

---

**Last Updated**: December 20, 2025 - Migrated from probability to intensity-based emotion system (low/medium/high with 3-star display)
