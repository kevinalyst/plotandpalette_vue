# Story Generation Job Flow Documentation

## Overview

Story generation in PlotAndPalette now uses the job-based async processing system, consistent with palette analysis and painting recommendations. This document describes the complete end-to-end flow from when the user clicks "All done!" to when they see their personalized story.

**Last Updated:** December 23, 2025

---

## Architecture Summary

```
User clicks "All done!" 
  → Save selection to DB
  → Create STORY_GENERATION job
  → Backend enriches data from database
  → Convert painting URLs to public URLs
  → Trigger n8n webhook
  → n8n calls Story API
  → n8n sends callback
  → Frontend polls and receives result
  → Navigate to StoryPage
```

---

## Complete Flow Step-by-Step

### **Phase 1: Frontend Validation & Selection Save**

**File:** `apps/frontend/src/views/GalleryPage.vue`

**When:** User clicks "All done!" button

**Actions:**

1. **Validate requirements:**
   - 3 paintings selected ✅
   - Character chosen ✅
   - Nickname entered ✅

2. **Save selection to database:**

```javascript
const selectionData = {
  selectedPaintings: validPaintings,  // Array of 3 painting objects
  character: selectedCharacter.value, // e.g., "historian"
  nickname: nickname.value,           // e.g., "Kevin"
  emotion: pageData.value.selectedEmotion,
  probability: pageData.value.selectedProbability,
  sessionId: sessionId
}

await ApiService.saveSelection(selectionData)
```

**API Call:** `POST /api/save-selection`

**Database Table:** `painting_selections`

**Stored Data:**
```sql
INSERT INTO painting_selections (
  session_id,
  selected_paintings,  -- JSON array of 3 paintings
  story_character,     -- Character type
  nickname,            -- User's chosen name
  created_at
) VALUES (?, ?, ?, ?, ?)
```

---

### **Phase 2: Create Story Generation Job**

**File:** `apps/frontend/src/views/GalleryPage.vue`

**Frontend creates minimal job:**

```javascript
const job = await ApiService.createJob({
  type: 'STORY_GENERATION',
  session_id: sessionId,
  input_data: {
    // Minimal data - backend will enrich from database
    sessionId: sessionId
  }
})

const jobId = job.data.job_id
```

**Why minimal data?**
- Selection already saved in database
- Backend has access to complete data
- Avoids data duplication
- Single source of truth (database)

---

### **Phase 3: Backend Database Enrichment**

**File:** `apps/frontend/functions/api/jobs/index.ts`

**When:** Job creation request received with type `STORY_GENERATION`

**Backend actions:**

```typescript
if (body.type === 'STORY_GENERATION') {
  // 1. Query painting selection
  const selection = await env.DB
    .prepare('SELECT selected_paintings, story_character, nickname FROM painting_selections WHERE session_id = ? ORDER BY created_at DESC LIMIT 1')
    .bind(body.session_id)
    .first();
  
  // 2. Parse paintings JSON
  const paintings = JSON.parse(selection.selected_paintings);
  
  // 3. Convert URLs to public URLs
  const origin = new URL(request.url).origin;
  const paintingsWithPublicUrls = paintings.map(painting => ({
    ...painting,
    url: convertToPublicUrl(painting.url, origin),
    originalUrl: painting.url
  }));
  
  // 4. Query emotion data
  const emotion = await env.DB
    .prepare('SELECT selected_emotion, intensity FROM emotion_selections WHERE session_id = ? ORDER BY created_at DESC LIMIT 1')
    .bind(body.session_id)
    .first();
  
  // 5. Build enriched payload
  const enrichedInputData = {
    paintings: paintingsWithPublicUrls,
    character: selection.story_character,
    nickname: selection.nickname,
    emotion: emotion?.selected_emotion || 'neutral',
    intensity: emotion?.intensity || 'medium',
    sessionId: body.session_id
  };
}
```

---

### **Phase 4: URL Conversion (Critical for n8n)**

**Purpose:** Convert relative painting URLs to fully qualified public URLs so n8n's AI agent can access them.

**Helper Function:**

```typescript
function convertToPublicUrl(url: string, origin: string): string {
  // Already a full URL? Return as-is
  if (url.startsWith('http://') || url.startsWith('https://')) {
    return url;
  }
  
  // Convert relative to absolute
  if (url.startsWith('/')) {
    return `${origin}${url}`;
  } else {
    return `${origin}/${url}`;
  }
}
```

**Example Conversions:**

| Original URL | Public URL |
|-------------|------------|
| `/api/assets/paintings/1.jpg` | `https://your-app.pages.dev/api/assets/paintings/1.jpg` |
| `/api/assets/paintings/45.jpg` | `https://your-app.pages.dev/api/assets/paintings/45.jpg` |
| `https://example.com/image.jpg` | `https://example.com/image.jpg` (unchanged) |

**Why this matters:**
- n8n runs on external server
- Can't access relative URLs
- AI agent needs to "see" the paintings
- Public URLs are directly accessible

---

### **Phase 5: Trigger n8n Webhook**

**File:** `apps/frontend/functions/api/jobs/index.ts`

**Payload sent to n8n:**

```json
{
  "job_id": "job-uuid-123",
  "job_type": "STORY_GENERATION",
  "session_id": "session-uuid-456",
  "input_data": {
    "paintings": [
      {
        "id": "123",
        "title": "Starry Night",
        "artist": "Vincent van Gogh",
        "year": "1889",
        "url": "https://your-app.pages.dev/api/assets/paintings/1.jpg",
        "originalUrl": "/api/assets/paintings/1.jpg",
        "page": "https://artsandculture.google.com/asset/..."
      },
      {
        "id": "124",
        "title": "The Scream",
        "artist": "Edvard Munch",
        "year": "1893",
        "url": "https://your-app.pages.dev/api/assets/paintings/45.jpg",
        "originalUrl": "/api/assets/paintings/45.jpg",
        "page": "https://artsandculture.google.com/asset/..."
      },
      {
        "id": "125",
        "title": "The Kiss",
        "artist": "Gustav Klimt",
        "year": "1908",
        "url": "https://your-app.pages.dev/api/assets/paintings/89.jpg",
        "originalUrl": "/api/assets/paintings/89.jpg",
        "page": "https://artsandculture.google.com/asset/..."
      }
    ],
    "character": "historian",
    "nickname": "Kevin",
    "emotion": "joy",
    "intensity": "high",
    "sessionId": "session-uuid-456"
  },
  "callback_url": "https://your-app.pages.dev/api/internal/jobs/job-uuid-123/callback"
}
```

**Headers:**
```
Content-Type: application/json
X-Shared-Secret: {N8N_SHARED_SECRET}
```

---

### **Phase 6: n8n Workflow Processing**

**n8n Workflow Steps:**

```
1. Webhook Trigger
   └─> Receives job payload
   └─> Validates X-Shared-Secret

2. Switch Node (job_type routing)
   └─> Case: PALETTE_ANALYSIS → [existing]
   └─> Case: PAINTING_RECOMMENDATION → [existing]
   └─> Case: STORY_GENERATION → [NEW]

3. HTTP Request: Story API
   └─> POST http://story-api:8000/generate-story
   └─> Body: {{ $json.input_data }}

4. Process Response
   └─> Extract story text
   └─> Format metadata

5. HTTP Request: Callback
   └─> POST {{ $json.callback_url }}
   └─> Headers: X-N8N-Signature (HMAC)
   └─> Body: Result payload
```

---

### **Phase 7: Story API Processing**

**External Service:** `apps/api/story_generation/story_api.py`

**Input:**
```python
{
  "paintings": [...],
  "character": "historian",
  "nickname": "Kevin",
  "emotion": "joy",
  "intensity": "high"
}
```

**Processing:**
- Uses AI/LLM to generate creative story
- Incorporates all 3 paintings
- Matches character style/personality
- Personalizes with user's nickname
- Considers emotional context

**Output:**
```python
{
  "story": "Once upon a time, in a world painted with joy...",
  "word_count": 450,
  "generation_time": 3.2
}
```

---

### **Phase 8: n8n Callback**

**n8n sends result back to Cloudflare:**

**Endpoint:** `POST /api/internal/jobs/{job_id}/callback`

**Headers:**
```
Content-Type: application/json
X-N8N-Signature: HMAC-SHA256(body, N8N_CALLBACK_SECRET)
```

**Body:**
```json
{
  "job_id": "job-uuid-123",
  "success": true,
  "result_data": {
    "story": "Once upon a time, in a world painted with joy, there lived a historian named Kevin...",
    "metadata": {
      "word_count": 450,
      "generation_time": 3.2
    }
  }
}
```

---

### **Phase 9: Backend Callback Processing**

**File:** `apps/frontend/functions/api/internal/jobs/[job_id]/callback.ts`

**Actions:**

1. **Verify HMAC signature:**
```typescript
const signature = request.headers.get('X-N8N-Signature');
const isValid = await verifyN8nCallback(env, body, signature);
if (!isValid) return errorResponse('Invalid signature', 401);
```

2. **Update job status in D1:**
```typescript
await updateJobStatus(env.DB, job_id, {
  status: 'COMPLETED',
  result_data: JSON.stringify(result_data),
  completed_at: new Date().toISOString()
});
```

3. **Save result to job_results table:**
```sql
INSERT INTO job_results (
  job_id,
  result_data,
  created_at
) VALUES (?, ?, ?)
```

---

### **Phase 10: Frontend Polling & Navigation**

**File:** `apps/frontend/src/views/GalleryPage.vue`

**Polling loop:**

```javascript
// Poll for completion (max 2 minutes: 60 attempts x 2 seconds)
const result = await ApiService.pollJob(jobId, 60, 2000)

// ApiService.pollJob implementation:
async pollJob(jobId, maxAttempts = 60, interval = 1000) {
  for (let i = 0; i < maxAttempts; i++) {
    const response = await this.getJob(jobId)
    
    if (response.data && response.data.status === 'COMPLETED') {
      return response.data.result_data
    } else if (response.data && response.data.status === 'FAILED') {
      throw new Error(response.data.error_message || 'Job failed')
    }
    
    // Wait before next poll
    await new Promise(resolve => setTimeout(resolve, interval))
  }
  
  throw new Error(`Job polling timeout after ${maxAttempts} attempts`)
}
```

**When job completes:**

```javascript
// Navigate to StoryPage with result
const storyPageData = {
  ...pageData.value,
  selectedPaintings: validPaintings,
  selectedCharacter: selectedCharacter.value,
  userName: nickname.value,
  story: result,  // Contains the generated story
  sessionId: sessionId
}

router.push({
  name: 'StoryPage',
  query: { data: unicodeSafeBase64Encode(JSON.stringify(storyPageData)) }
})
```

---

## Database Schema

### painting_selections Table

```sql
CREATE TABLE painting_selections (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id TEXT NOT NULL,
  selected_paintings TEXT NOT NULL,  -- JSON array
  story_character TEXT,
  nickname TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);
```

### jobs Table

```sql
CREATE TABLE jobs (
  job_id TEXT PRIMARY KEY,
  session_id TEXT NOT NULL,
  type TEXT NOT NULL,              -- 'STORY_GENERATION'
  status TEXT NOT NULL,            -- 'QUEUED' → 'RUNNING' → 'COMPLETED'
  client_request_id TEXT,
  input_data TEXT NOT NULL,        -- Enriched payload JSON
  created_at TEXT NOT NULL,
  started_at TEXT,
  completed_at TEXT,
  error_message TEXT,
  FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);
```

### job_results Table

```sql
CREATE TABLE job_results (
  job_id TEXT PRIMARY KEY,
  result_data TEXT NOT NULL,       -- Story + metadata JSON
  r2_result_key TEXT,
  created_at TEXT NOT NULL,
  FOREIGN KEY (job_id) REFERENCES jobs(job_id)
);
```

---

## Error Handling

### Frontend Errors

**Validation errors:**
- Missing paintings: Alert user to select 3 paintings
- No character: Alert user to select character
- No nickname: Alert user to enter nickname

**API errors:**
- Selection save fails: Alert with error message
- Job creation fails: Alert with error message
- Polling timeout (2 minutes): Alert "Story generation taking too long"

**Error display:**
```javascript
} catch (error) {
  console.error('❌ Error generating story:', error)
  alert(`Failed to generate story: ${error.message}`)
} finally {
  loading.value = false
  generatingStory.value = false
  spinnerType.value = 'magic-cube'
}
```

### Backend Errors

**Database errors:**
- No selection found: Return 404 "No painting selection found for this session"
- Query fails: Return 500 with error message

**n8n webhook errors:**
- Webhook fails: Log error, don't fail job creation
- Job still created, can be retried

---

## Performance Metrics

**Expected Timings:**

| Phase | Duration |
|-------|----------|
| Save selection | < 100ms |
| Create job | < 200ms |
| Database enrichment | < 100ms |
| Trigger n8n | < 500ms |
| Story API processing | 2-10 seconds |
| n8n callback | < 500ms |
| Update database | < 100ms |
| Frontend polling | 2-15 seconds (cumulative) |
| **Total** | **~3-15 seconds** |

**Polling Configuration:**
- Max attempts: 60
- Interval: 2 seconds
- Timeout: 2 minutes (120 seconds)

---

## Testing Checklist

- [ ] User selects 3 paintings
- [ ] User selects character
- [ ] User enters nickname
- [ ] Click "All done!" button
- [ ] Selection saves to database
- [ ] Job creates with status QUEUED
- [ ] Backend queries selection from database
- [ ] Backend queries emotion from database
- [ ] Painting URLs convert to public URLs
- [ ] n8n webhook receives enriched payload
- [ ] Story API processes request successfully
- [ ] n8n sends callback with story
- [ ] Callback signature verifies
- [ ] Job status updates to COMPLETED
- [ ] Result saves to job_results table
- [ ] Frontend polling receives result
- [ ] Navigate to StoryPage with story
- [ ] Story displays correctly

**Error scenarios:**
- [ ] No paintings selected → Alert
- [ ] Only 1-2 paintings selected → Alert
- [ ] No character selected → Alert
- [ ] No nickname entered → Alert
- [ ] Database save fails → Alert with error
- [ ] Job creation fails → Alert with error
- [ ] Polling timeout → Alert with timeout message
- [ ] Story API fails → Job status = FAILED
- [ ] Invalid callback signature → Rejected

---

## Key Benefits of This Architecture

1. **Consistency:** Story generation uses same pattern as palette analysis & recommendations
2. **Database as Source of Truth:** Selection loaded from database, not passed through frontend
3. **Public URL Access:** AI agent can directly access painting images via public URLs
4. **Async Processing:** Long-running story generation doesn't block UI
5. **Status Tracking:** User sees real-time status during generation
6. **Error Recovery:** Failed jobs visible in database, can be retried
7. **Scalability:** n8n handles load distribution and retries
8. **Separation of Concerns:** Frontend → Database → Backend → n8n → Story API

---

## Environment Variables Required

**Cloudflare Worker (.dev.vars / Pages settings):**
```
N8N_WEBHOOK_URL=https://your-n8n-instance.com/webhook/story-generation
N8N_SHARED_SECRET=supersecretkey123
N8N_CALLBACK_SECRET=anothersecretkey456
```

**n8n Workflow:**
```
CLOUDFLARE_CALLBACK_SECRET=anothersecretkey456  # For HMAC signing
STORY_API_URL=http://story-api:8000/generate-story
```

---

## Related Documentation

- [PROJECT_PROGRESS_SUMMARY.md](./PROJECT_PROGRESS_SUMMARY.md) - Overall project status
- [ENDPOINTS-DOCUMENTATION.md](./ENDPOINTS-DOCUMENTATION.md) - API endpoint reference
- [RELOAD_RECOMMENDATIONS_FIX.md](./RELOAD_RECOMMENDATIONS_FIX.md) - Similar job-based pattern
- [N8N_PAINTING_RECOMMENDATIONS.md](./N8N_PAINTING_RECOMMENDATIONS.md) - n8n workflow setup

---

## Future Enhancements

1. **Retry mechanism:** Allow users to regenerate story with same selections
2. **Story variants:** Generate multiple story versions, let user choose
3. **Progress updates:** Real-time progress during story generation
4. **Story editing:** Allow user to request modifications
5. **Story sharing:** Generate shareable link to story
6. **Story history:** View all previously generated stories
7. **Export options:** Download story as PDF, image, or text file

---

**Implementation Complete:** December 23, 2025
