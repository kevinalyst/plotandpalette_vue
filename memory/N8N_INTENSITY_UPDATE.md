# n8n Intensity System Update

## ⚠️ BREAKING CHANGE: Probability → Intensity

The emotion prediction system has been migrated from **probability percentages** to **intensity levels**.

---

## What Changed

### Old System (DEPRECATED ❌)
```json
{
  "emotionPrediction": {
    "emotion": "happiness",
    "all_probabilities": {
      "happiness": 0.87,
      "love": 0.45,
      "optimism": 0.23
    }
  }
}
```

### New System (REQUIRED ✅)
```json
{
  "emotionPrediction": {
    "emotion": "happiness",
    "all_intensities": {
      "happiness": "high",
      "love": "medium",
      "optimism": "low"
    }
  }
}
```

---

## n8n Workflow Updates Required

### 1. Update PALETTE_ANALYSIS Callback

Your n8n workflow must return `all_intensities` (not `all_probabilities`):

**Required Format:**
```json
{
  "success": true,
  "result_data": {
    "filename": "screenshot-123.png",
    "rawColors": {
      "#8b54b5": 0.1027,
      "#ffc0cb": 0.2515
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

---

## Converting Probabilities to Intensities

If your ML model returns probabilities, convert them:

**Mapping Logic:**
```python
def probability_to_intensity(prob):
    if prob >= 0.67:
        return "high"
    elif prob >= 0.34:
        return "medium"
    else:
        return "low"

# Example:
all_probabilities = {
    "happiness": 0.87,    # → "high"
    "love": 0.45,         # → "medium"
    "optimism": 0.23      # → "low"
}

all_intensities = {
    emotion: probability_to_intensity(prob)
    for emotion, prob in all_probabilities.items()
}
```

---

## Frontend Display

The intensity levels are displayed as **3-star ratings**:

| Intensity | Stars | Display |
|-----------|-------|--------|
| `"high"` | ★★★ | 3 filled stars |
| `"medium"` | ★★☆ | 2 filled stars |
| `"low"` | ★☆☆ | 1 filled star |

---

## All 15 Emotions Required

Your callback **must include all 15 emotions** with intensity values:

1. happiness
2. love
3. optimism
4. trust
5. anticipation
6. surprise
7. fear
8. sadness
9. anger
10. disgust
11. gratitude
12. humility
13. arrogance
14. pessimism
15. disagreeableness

---

## Database Changes

**New Column:**
- `emotion_selections.intensity` (TEXT) - stores "low", "medium", or "high"

**Deprecated (kept for compatibility):**
- `emotion_selections.probability` (REAL) - no longer used by frontend

---

## Testing Your n8n Workflow

### Test Callback Payload

```bash
curl -X POST \
  "https://your-cloudflare-deployment.pages.dev/api/internal/jobs/test-job-id/callback" \
  -H "Content-Type: application/json" \
  -H "X-N8N-Signature: your-hmac-signature" \
  -d '{
    "success": true,
    "result_data": {
      "filename": "test.png",
      "rawColors": {"#ff0000": 0.5, "#00ff00": 0.5},
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

## Migration Applied

✅ Database migration completed: `0002_add_intensity_column.sql`

**Applied to**: `plotandplate-db` (7447da98-cd99-4dba-9b09-0f804e34c51b)

---

## Deployment

✅ **Live at**: https://086c2e1b.plotandpalette-vue-local.pages.dev

**Updated Files:**
- `apps/frontend/src/views/ColorPalettePage.vue` - 3-star display
- `apps/frontend/functions/api/save-emotion.ts` - intensity validation
- `apps/frontend/functions/api/emotions.ts` - intensity validation
- `apps/frontend/functions/lib/db.ts` - saveEmotionSelection() uses intensity
- `ENDPOINTS-DOCUMENTATION.md` - updated API specs

---

**Next Step**: Update your n8n PALETTE_ANALYSIS workflow to return `all_intensities` instead of `all_probabilities`!
