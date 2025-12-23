# n8n Painting Recommendations Integration Guide

**Feature:** Two-Stage Callback with AI-Enhanced Recommendations  
**Date:** December 22, 2025  
**Status:** Ready for Implementation

---

## 🎯 Architecture Overview

### **Two-Stage Callback Strategy:**

**Stage 1 - Quick Emotion Response (2-3s):**
- Google Vision extracts colors
- Emotion prediction runs
- **Callback #1** returns emotions + colors
- User sees ColorPalettePage immediately! ✅

**Stage 2 - Background Recommendations (additional 1.5s):**
- Worker computes top 50 color-similar paintings
- AI agent selects best 10 based on emotion
- **Callback #2** adds recommendations to same job
- User browses emotions while this completes
- GalleryPage loads instantly when user clicks "Continue"! ✅

---

## 📋 n8n Workflow Configuration

### **Updated Node Flow:**

```
Webhook
  ↓
Switch (job_type)
  ↓
Binary Data (get screenshot)
  ↓
Parse Base64
  ↓
Google Vision API
  ↓
Convert Color Data
  ↓
┌─────────────────────────────────────────┐
│  PARALLEL SPLIT (or Sequential)        │
├─────────────────────────────────────────┤
│                                         │
│  Branch A: Emotion Prediction           │
│    ↓                                    │
│  Callback #1 (QUICK - emotions only)    │
│    ↓                                    │
│  Wait 500ms                             │
│                                         │
│  Branch B: (continues after wait)       │
│    ↓                                    │
│  HTTP: Get Top 50 Recommendations       │
│    ↓                                    │
│  AI Agent: Select Best 10               │
│    ↓                                    │
│  Callback #2 (adds recommendations)     │
└─────────────────────────────────────────┘
```

---

## 🔧 Node Configurations

### **Node 1: "Get Top 50 Recommendations"**

**Type:** HTTP Request  
**Method:** POST  
**When to Execute:** After "Emotion Prediction" + Wait 500ms

**URL:**
```
https://your-app.pages.dev/api/recommendations/compute
```

**Authentication:**
```
Type: Header Auth
Header Name: X-API-Key
Value: {{ $env.CLOUDFLARE_API_KEY }}
```

**Headers:**
```json
{
  "Content-Type": "application/json"
}
```

**Body (JSON):**
```javascript
{
  "rawColors": {{ $('Convert Color Data').item.json.rawColors }}
}
```

**Expected Response:**
```json
{
  "success": true,
  "total_candidates": 50,
  "total_artworks_analyzed": 155,
  "candidates": [
    {
      "id": 42,
      "artist": "王玉平",
      "title": "梦",
      "year": "1992",
      "r2_key": "paintings/chinese-contemporary/42.jpg",
      "similarity_score": 0.9234,
      "colors": [
        {"r": 155, "g": 212, "b": 207, "percentage": 0.3863},
        ...
      ]
    },
    // ... 49 more
  ]
}
```

---

### **Node 2: "AI Select Best 10 Paintings"** (Optional but Recommended)

**Type:** OpenRouter Chat / AI Agent  
**Model:** GPT-4 or similar

**System Prompt:**
```
You are an art curator with expertise in Chinese contemporary art and color psychology.
```

**User Prompt:**
```javascript
Here are 50 paintings pre-selected by color similarity to the user's palette.
The user's dominant emotion is: {{ $('Emotion Prediction').item.json.primary_emotion || 'neutral' }}

Your task: Select exactly 10 paintings that best match this emotion.

Consider:
1. Color harmony with the emotion (warm/cool tones, saturation, brightness)
2. Artwork style and mood suggested by the title
3. Artist's typical emotional expression
4. Balance and diversity in the final selection

Paintings data:
{{ JSON.stringify($('Get Top 50 Recommendations').item.json.candidates) }}

Respond ONLY with a JSON array of 10 painting IDs (integers), ordered from best to good match:
[42, 17, 89, ...]
```

**Output Parsing:**
```javascript
// In next node: "Format Final Recommendations"
const aiSelectedIds = JSON.parse($('AI Select Best 10 Paintings').item.json.choices[0].message.content);

const allCandidates = $('Get Top 50 Recommendations').item.json.candidates;

const finalRecommendations = aiSelectedIds.map(id => 
  allCandidates.find(p => p.id === id)
).filter(Boolean);

return { 
  json: { 
    detailedRecommendations: finalRecommendations 
  } 
};
```

---

### **Node 3: "Callback #2 - Add Recommendations"**

**Type:** HTTP Request  
**Method:** POST  
**When to Execute:** After AI selects final 10

**URL:**
```javascript
{{ $('Webhook').item.json.callback_url }}
```

**Authentication:**
```
Type: None (HMAC signature handled by Crypto node)
```

**Headers:**
```javascript
{
  "Content-Type": "application/json",
  "X-N8N-Signature": {{ $('Crypto for Recommendations').item.json.signature }}
}
```

**Body:**
```javascript
{
  "success": true,
  "result_data": {
    "detailedRecommendations": {{ $('Format Final Recommendations').item.json.detailedRecommendations }}
  }
}
```

**Important:** This callback **merges** with existing data from Callback #1!

---

## 📊 Complete Callback Payloads

### **Callback #1 (Emotion Stage):**

```json
{
  "success": true,
  "result_data": {
    "filename": "screenshots/session-id/capture-123.png",
    "rawColors": {
      "#8b54b5": 0.1027,
      "#ffc0cb": 0.2515,
      ...
    },
    "colourData": {
      "purple": 0.10,
      "pink": 0.25,
      ...
    },
    "emotionPrediction": {
      "all_intensities": {
        "happiness": "high",
        "love": "medium",
        ...
      }
    }
    // NO detailedRecommendations yet!
  }
}
```

**Job Status After Callback #1:** `COMPLETED`  
**Frontend Action:** Shows ColorPalettePage with emotions ✅

---

### **Callback #2 (Recommendations Stage):**

```json
{
  "success": true,
  "result_data": {
    "detailedRecommendations": [
      {
        "id": 42,
        "title": "梦",
        "artist": "王玉平",
        "year": "1992",
        "url": "/api/assets/paintings/chinese-contemporary/42.jpg",
        "page": null,
        "similarity_score": 0.9234
      },
      // ... 9 more (10 total)
    ]
  }
}
```

**Job Status After Callback #2:** Still `COMPLETED` (merged data)  
**Frontend Action:** GalleryPage loads with paintings when user navigates ✅

---

## 🔄 n8n Node Sequence

### **Recommended Setup:**

1. **Webhook** (trigger)
2. **Switch** (route by job_type)
3. **Binary Data** (extract screenshot)
4. **Parse Base64**
5. **Google Vision API**
6. **Convert Color Data**
7. **Emotion Prediction** (OpenRouter/LLM)
8. **Callback #1 Body** (Code node - build first callback)
9. **Crypto #1** (HMAC sign for first callback)
10. **HTTP: Send Callback #1** ← **User sees emotions!**
11. **Wait 500ms** (give first callback time to save)
12. **HTTP: Get Top 50** (call /api/recommendations/compute)
13. **AI Select Best 10** (OpenRouter - choose from 50)
14. **Format Recommendations** (Code - structure for callback)
15. **Callback #2 Body** (Code - build second callback)
16. **Crypto #2** (HMAC sign for second callback)
17. **HTTP: Send Callback #2** ← **Recommendations ready!**

---

## 💻 Code Snippets for n8n Nodes

### **Callback #1 Body (Code Node):**

```javascript
const webhook = $('Webhook').item.json;
const colors = $('Convert Color Data').item.json;
const emotions = $('Emotion Prediction').item.json;

return {
  json: {
    success: true,
    result_data: {
      filename: webhook.input_data.screenshot_key,
      rawColors: colors.rawColors,
      colourData: colors.colourData,
      emotionPrediction: {
        all_intensities: emotions.all_intensities
      }
      // NO recommendations in first callback!
    }
  }
};
```

---

### **AI Selection Prompt (Detailed):**

```
You are curating a personalized art exhibition for a user.

User's Emotion: {{ $('Emotion Prediction').item.json.primary_emotion }}
(with intensity: {{ $('Emotion Prediction').item.json.all_intensities[primary_emotion] }})

From these 50 pre-selected paintings (chosen by color similarity), select exactly 10 that best resonate with this emotion.

Guidelines:
- For "happiness" (high): Choose vibrant, warm, uplifting colors
- For "sadness" (medium/high): Choose cooler tones, contemplative compositions
- For "love" (high): Choose warm pinks, reds, intimate scenes
- For "fear" (medium/high): Choose darker palettes, tension in composition

The 50 candidates:
{{ JSON.stringify($('Get Top 50 Recommendations').item.json.candidates, null, 2) }}

Respond with ONLY a JSON array of 10 painting IDs (no markdown, no explanation):
[42, 17, 89, 5, 123, 67, 91, 34, 78, 112]
```

---

### **Format Recommendations (Code Node):**

```javascript
// Parse AI response
const aiResponse = $('AI Select Best 10 Paintings').item.json.choices[0].message.content;
const selectedIds = JSON.parse(aiResponse);

// Get full painting data from top 50
const allCandidates = $('Get Top 50 Recommendations').item.json.candidates;

// Map IDs to full painting objects
const finalPaintings = selectedIds.map(id => {
  const painting = allCandidates.find(p => p.id === id);
  
  if (!painting) return null;
  
  // Format for frontend
  return {
    id: painting.id,
    title: painting.title,
    artist: painting.artist,
    year: painting.year,
    url: `/api/assets/${painting.r2_key}`,
    page: null, // No external page for Chinese Contemporary Art
    similarity_score: painting.similarity_score
  };
}).filter(Boolean);

return {
  json: {
    detailedRecommendations: finalPaintings.slice(0, 10) // Ensure exactly 10
  }
};
```

---

### **Callback #2 Body (Code Node):**

```javascript
const recommendations = $('Format Recommendations').item.json;

return {
  json: {
    success: true,
    result_data: {
      detailedRecommendations: recommendations.detailedRecommendations
    }
  }
};
```

---

## ⏱️ Performance Timeline

```
t=0ms:    User captures palette
t=100ms:  Job created, n8n triggered
t=2000ms: Emotion prediction complete
t=2100ms: CALLBACK #1 sent
t=2200ms: User sees ColorPalettePage! ✅
t=2700ms: Top 50 paintings computed (parallel)
t=3700ms: AI selects best 10
t=3800ms: CALLBACK #2 sent
t=3900ms: Recommendations ready in database

User browses emotions for ~20-30 seconds

t=30000ms: User clicks "Continue"
t=30100ms: GalleryPage loads INSTANTLY! ✅ (data already ready)
```

**Total latency perceived by user:** 2.2 seconds to emotions, 0ms to gallery!

---

## 🧪 Testing the Integration

### **Test 1: Quick Emotion Callback**

```bash
# Trigger workflow, check job after 3 seconds
curl "https://your-app.pages.dev/api/jobs/test-job-id"

# Should have:
# - status: "COMPLETED"
# - result_data.emotionPrediction ✅
# - result_data.detailedRecommendations ❌ (not yet)
```

### **Test 2: Recommendations Added**

```bash
# Check same job after 5 seconds
curl "https://your-app.pages.dev/api/jobs/test-job-id"

# Should have:
# - status: "COMPLETED"
# - result_data.emotionPrediction ✅
# - result_data.detailedRecommendations ✅ (now present!)
```

---

## 🐛 Troubleshooting

### **Issue: Second callback overwrites first**

**Cause:** Callback handler not merging  
**Solution:** Already fixed! Handler now merges result_data ✅

### **Issue: AI returns wrong format**

**Cause:** AI returns markdown or explanation  
**Solution:** Add parsing logic:
```javascript
let ids;
try {
  ids = JSON.parse(aiResponse);
} catch (e) {
  // Try extracting array from markdown
  const match = aiResponse.match(/\[[\d,\s]+\]/);
  if (match) {
    ids = JSON.parse(match[0]);
  }
}
```

### **Issue: Top 50 API times out**

**Cause:** D1 query slow or too many paintings  
**Solution:** Check database has colors populated:
```bash
npx wrangler d1 execute plotandplate-db --remote --command="SELECT COUNT(*) FROM art_information WHERE color_r_1 > 0"
# Should return 155
```

---

## 📊 API Contract

### **Recommendation API:**

**Endpoint:** `POST /api/recommendations/compute`

**Request:**
```typescript
{
  rawColors: Array<{
    r: number;        // 0-255
    g: number;        // 0-255
    b: number;        // 0-255
    percentage: number; // 0.0-1.0
  }> // Exactly 5 colors
}
```

**Response:**
```typescript
{
  success: boolean;
  total_candidates: number;      // Should be 50
  total_artworks_analyzed: number; // Should be 155
  candidates: Array<{
    id: number;
    artist: string;
    title: string;
    year: string;
    r2_key: string;
    similarity_score: number;  // 0.0-1.0
    colors: RawColor[];        // 5 colors with full data
  }>
}
```

---

## ✅ Deployment Checklist

- [x] `/api/recommendations/compute` endpoint created
- [x] Cosine similarity algorithm implemented
- [x] Callback handler supports merging
- [ ] Deploy to Cloudflare Pages
- [ ] Configure n8n nodes
- [ ] Test two-stage callback
- [ ] Verify frontend displays both emotions and paintings

---

## 🎨 Example: Complete n8n Response

**After Both Callbacks Complete:**

Frontend receives from GET `/api/jobs/{job_id}`:

```json
{
  "job_id": "abc-123",
  "type": "PALETTE_ANALYSIS",
  "status": "COMPLETED",
  "result_data": {
    // From Callback #1:
    "filename": "screenshots/session/capture.png",
    "rawColors": {...},
    "colourData": {...},
    "emotionPrediction": {
      "all_intensities": {...}
    },
    
    // From Callback #2 (merged):
    "detailedRecommendations": [
      {
        "id": 42,
        "title": "梦",
        "artist": "王玉平",
        "year": "1992",
        "url": "/api/assets/paintings/chinese-contemporary/42.jpg",
        "similarity_score": 0.9234
      },
      // ... 9 more
    ]
  },
  "created_at": "...",
  "completed_at": "..."
}
```

---

## 🚀 Ready to Configure?

1. Deploy latest code: `cd apps/frontend && npx wrangler pages deploy`
2. Add nodes to your n8n workflow following configurations above
3. Test with a real palette capture
4. Verify two callbacks arrive and merge correctly

Good luck! 🎨
