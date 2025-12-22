# n8n PALETTE_ANALYSIS Response Schema

**Endpoint:** POST `/api/internal/jobs/:job_id/callback`  
**Job Type:** `PALETTE_ANALYSIS`  
**Last Updated:** December 20, 2025

---

## Required Response Format

```json
{
  "success": true,
  "result_data": {
    "filename": "screenshots/session-uuid/capture-1234567890.png",
    "rawColors": {
      "#a388f5": 0.3456663871647036,
      "#9071f3": 0.19848732998823648,
      "#c5b2f9": 0.17886344637669988,
      "#e0d6fc": 0.15331153478708373,
      "#e9e3fe": 0.12367130168327616
    },
    "colourData": {
      "blue": 0.5441537171529403,
      "purple": 0.3321749811637837,
      "grey": 0.12367130168327618
    },
    "emotionPrediction": {
      "all_intensities": {
        "happiness": "high",
        "love": "medium",
        "optimism": "high",
        "trust": "low",
        "anticipation": "medium",
        "surprise": "medium",
        "gratitude": "medium",
        "fear": "low",
        "sadness": "low",
        "anger": "low",
        "disgust": "low",
        "pessimism": "low",
        "humility": "medium",
        "arrogance": "medium",
        "disagreeableness": "low"
      }
    },
    "clusters": {
      "cluster_0": "{\"hex\":\"#a388f5\",\"rgb\":{\"r\":163,\"g\":136,\"b\":245},\"pixelFraction\":0.14833333}",
      "cluster_1": "{\"hex\":\"#9071f3\",\"rgb\":{\"r\":144,\"g\":113,\"b\":243},\"pixelFraction\":0.08517544}",
      "cluster_2": "{\"hex\":\"#c5b2f9\",\"rgb\":{\"r\":197,\"g\":178,\"b\":249},\"pixelFraction\":0.076754384}",
      "cluster_3": "{\"hex\":\"#e0d6fc\",\"rgb\":{\"r\":224,\"g\":214,\"b\":252},\"pixelFraction\":0.065789476}",
      "cluster_4": "{\"hex\":\"#e9e3fe\",\"rgb\":{\"r\":233,\"g\":227,\"b\":254},\"pixelFraction\":0.053070176}"
    }
  }
}
```

**Note:** Color extraction now uses **Google Vision API** (free 1,000 requests/month) instead of Imagga ($79/month).

---

## Field Specifications

### Top Level

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `success` | boolean | ✅ Yes | `true` if analysis succeeded, `false` if failed |
| `result_data` | object | ✅ Yes | Contains all analysis results (see below) |
| `error_message` | string | Only if `success: false` | Error description when analysis fails |

### result_data Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `filename` | string | ✅ Yes | Original screenshot filename |
| `rawColors` | object | ✅ Yes | Hex color codes with their proportions (0-1) |
| `colourData` | object | ✅ Yes | Named colors with their proportions (0-1) |
| `emotionPrediction` | object | ✅ Yes | Contains emotion intensity predictions |

### emotionPrediction Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `all_intensities` | object | ✅ Yes | All 15 emotions with intensity levels |

### all_intensities Object

Must contain **all 15 emotions** with intensity values:

| Emotion | Type | Allowed Values | Description |
|---------|------|----------------|-------------|
| `happiness` | string | `"low"` \| `"medium"` \| `"high"` | Intensity level |
| `love` | string | `"low"` \| `"medium"` \| `"high"` | Intensity level |
| `optimism` | string | `"low"` \| `"medium"` \| `"high"` | Intensity level |
| `trust` | string | `"low"` \| `"medium"` \| `"high"` | Intensity level |
| `anticipation` | string | `"low"` \| `"medium"` \| `"high"` | Intensity level |
| `surprise` | string | `"low"` \| `"medium"` \| `"high"` | Intensity level |
| `fear` | string | `"low"` \| `"medium"` \| `"high"` | Intensity level |
| `sadness` | string | `"low"` \| `"medium"` \| `"high"` | Intensity level |
| `anger` | string | `"low"` \| `"medium"` \| `"high"` | Intensity level |
| `disgust` | string | `"low"` \| `"medium"` \| `"high"` | Intensity level |
| `gratitude` | string | `"low"` \| `"medium"` \| `"high"` | Intensity level |
| `humility` | string | `"low"` \| `"medium"` \| `"high"` | Intensity level |
| `arrogance` | string | `"low"` \| `"medium"` \| `"high"` | Intensity level |
| `pessimism` | string | `"low"` \| `"medium"` \| `"high"` | Intensity level |
| `disagreeableness` | string | `"low"` \| `"medium"` \| `"high"` | Intensity level |

---

## Converting Probabilities to Intensities

If your ML model returns probabilities (0.0 - 1.0), convert them using:

```python
def probability_to_intensity(prob: float) -> str:
    """Convert probability to intensity level"""
    if prob >= 0.67:
        return "high"
    elif prob >= 0.34:
        return "medium"
    else:
        return "low"

# Example usage:
all_probabilities = {
    "happiness": 0.87,  # → "high"
    "love": 0.45,       # → "medium"
    "optimism": 0.23    # → "low"
}

all_intensities = {
    emotion: probability_to_intensity(prob)
    for emotion, prob in all_probabilities.items()
}
```

```javascript
// JavaScript/TypeScript version
function probabilityToIntensity(prob) {
    if (prob >= 0.67) return "high";
    if (prob >= 0.34) return "medium";
    return "low";
}

// Example:
const allProbabilities = {
    happiness: 0.87,  // → "high"
    love: 0.45,       // → "medium"
    optimism: 0.23    // → "low"
};

const allIntensities = Object.fromEntries(
    Object.entries(allProbabilities).map(([emotion, prob]) => 
        [emotion, probabilityToIntensity(prob)]
    )
);
```

---

## Frontend Display

The intensity levels are displayed as **3-star ratings**:

| Intensity | Stars | Display |
|-----------|-------|---------|
| `"high"` | ★★★ | 3 filled gold stars |
| `"medium"` | ★★☆ | 2 filled, 1 gray star |
| `"low"` | ★☆☆ | 1 filled, 2 gray stars |

---

## Error Response Format

When analysis fails, return:

```json
{
  "success": false,
  "error_message": "Failed to analyze palette: Invalid image format",
  "result_data": null
}
```

---

## Security: HMAC Signature

All callbacks must include HMAC-SHA256 signature:

**Header:** `X-N8N-Signature`  
**Algorithm:** HMAC-SHA256(JSON.stringify(body), N8N_CALLBACK_SECRET)

```python
# Python example
import hmac
import hashlib
import json

def create_signature(body_dict, secret):
    body_string = json.dumps(body_dict, separators=(',', ':'))
    signature = hmac.new(
        secret.encode(),
        body_string.encode(),
        hashlib.sha256
    ).hexdigest()
    return signature

# Usage:
headers = {
    'Content-Type': 'application/json',
    'X-N8N-Signature': create_signature(response_body, N8N_CALLBACK_SECRET)
}
```

---

## Complete n8n Workflow Example

### 1. Receive Webhook from Cloudflare
```json
{
  "job_id": "job-uuid",
  "session_id": "session-uuid",
  "job_type": "PALETTE_ANALYSIS",
  "input_data": {
    "screenshot_key": "screenshots/screenshot-123.png"
  },
  "callback_url": "https://your-app.pages.dev/api/internal/jobs/job-uuid/callback"
}
```

### 2. Process the Image
- Download screenshot from R2
- Extract colors
- Run ML emotion prediction model
- Convert probabilities to intensities

### 3. Send Callback
```http
POST /api/internal/jobs/job-uuid/callback
Content-Type: application/json
X-N8N-Signature: abc123...

{
  "success": true,
  "result_data": {
    "filename": "screenshot-123.png",
    "rawColors": { ... },
    "colourData": { ... },
    "emotionPrediction": {
      "all_intensities": { ... }
    }
  }
}
```

---

## Validation Checklist

Before deploying your n8n workflow, verify:

- [ ] Response includes all required top-level fields
- [ ] `emotionPrediction.all_intensities` includes all 15 emotions
- [ ] All intensity values are `"low"`, `"medium"`, or `"high"` (not numbers)
- [ ] `rawColors` object has hex keys (e.g., `"#ff0000"`)
- [ ] `colourData` object has named color keys (e.g., `"red"`)
- [ ] HMAC signature is calculated correctly
- [ ] Error responses include `error_message` when `success: false`

---

## Testing Your Callback

```bash
curl -X POST \
  "https://your-app.pages.dev/api/internal/jobs/test-job-id/callback" \
  -H "Content-Type: application/json" \
  -H "X-N8N-Signature: your-hmac-signature" \
  -d '{
    "success": true,
    "result_data": {
      "filename": "test.png",
      "rawColors": {
        "#ff0000": 0.5,
        "#00ff00": 0.5
      },
      "colourData": {
        "red": 0.5,
        "green": 0.5
      },
      "emotionPrediction": {
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
          "gratitude": "low",
          "humility": "low",
          "arrogance": "low",
          "pessimism": "low",
          "disagreeableness": "low"
        }
      }
    }
  }'
```

---

## Changes from Previous Version

**Removed Fields:**
- ❌ `emotionPrediction.emotion` - No longer needed (single emotion selection)
- ❌ `emotionPrediction.all_probabilities` - Replaced by intensities
- ❌ `r2_result_key` - Not needed for PALETTE_ANALYSIS (results are small)

**Kept Fields:**
- ✅ `emotionPrediction` wrapper object - Keeps frontend code working
- ✅ `all_intensities` - Core emotion data with "low"/"medium"/"high" values

---

## Related Documentation

- `N8N_INTENSITY_UPDATE.md` - Migration guide from probabilities to intensities
- `ENDPOINTS-DOCUMENTATION.md` - Complete API endpoint documentation
- `CLOUDFLARE_DEPLOYMENT_GUIDE.md` - Full deployment guide
- `apps/frontend/functions/api/internal/jobs/[job_id]/callback.ts` - Callback handler code

---

**Status:** ✅ Final Schema - Ready for n8n Implementation  
**Frontend Compatibility:** ✅ No changes required  
**Deployment:** https://086c2e1b.plotandpalette-vue-local.pages.dev
