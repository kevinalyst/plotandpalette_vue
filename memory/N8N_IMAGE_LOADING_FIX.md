# n8n Image Loading Fix - Screenshot URL Issue

**Date:** December 21, 2025  
**Issue:** Captured palette image returns 401 Unauthorized  
**Status:** ✅ Solution Ready

---

## Problem Summary

The frontend cannot load the captured screenshot because:

1. ✅ Screenshot uploads to R2 successfully → `screenshots/session-id/capture-123.png`
2. ✅ n8n receives the R2 key in `input_data.screenshot_key`
3. ❌ n8n callback sends only basename → `"filename": "capture-123.png"`
4. ❌ Frontend tries `/api/uploads/capture-123.png` → 401 (requires API key)
5. ❌ Should be `/api/assets/screenshots/session-id/capture-123.png` → Public

---

## The Fix: Update n8n Workflow

### Current n8n Callback (WRONG ❌)

```json
{
  "success": true,
  "result_data": {
    "filename": "capture-1766319125643.png",  ← WRONG: Only basename
    "rawColors": {...},
    "colourData": {...},
    "emotionPrediction": {...}
  }
}
```

### Fixed n8n Callback (CORRECT ✅)

```json
{
  "success": true,
  "result_data": {
    "filename": "screenshots/abc123-session-id/capture-1766319125643.png",  ← CORRECT: Full R2 key
    "rawColors": {...},
    "colourData": {...},
    "emotionPrediction": {...}
  }
}
```

---

## How to Fix Your n8n Workflow

### Step 1: Find the "Callback Body Object" Node

This is the node that constructs the callback payload before sending to Cloudflare.

### Step 2: Update the `filename` Field

**BEFORE (Wrong):**
```javascript
// If you're extracting just the filename:
filename: items[0].json.screenshot_key.split('/').pop()
// OR
filename: "capture-123.png"
```

**AFTER (Correct):**
```javascript
// Use the full screenshot_key from the webhook input:
filename: items[0].json.input_data.screenshot_key
// This will be something like: "screenshots/session-id/capture-123.png"
```

### Step 3: Verify the Full Flow

**Input from Cloudflare (what n8n receives):**
```json
{
  "job_id": "job-uuid",
  "session_id": "session-uuid",
  "job_type": "PALETTE_ANALYSIS",
  "input_data": {
    "screenshot_key": "screenshots/abc123/capture-1766319125643.png"  ← Use this!
  },
  "callback_url": "..."
}
```

**Output from n8n (what you send back):**
```json
{
  "success": true,
  "result_data": {
    "filename": "{{ $json.input_data.screenshot_key }}",  ← Pass it through!
    "rawColors": {...},
    "colourData": {...},
    "emotionPrediction": {...}
  }
}
```

---

## Why This Works

### URL Construction Flow

1. **Screenshot Upload** (`/api/uploads/screenshot`):
   - Returns: `{ key: "screenshots/session/capture-123.png", url: "/api/assets/screenshots/session/capture-123.png" }`

2. **Job Creation** (`GradientPalette.vue`):
   - Sends: `{ screenshot_key: "screenshots/session/capture-123.png" }`

3. **n8n Callback**:
   - Returns: `{ filename: "screenshots/session/capture-123.png" }`

4. **Frontend Display** (`ColorPalettePage.vue`):
   - Constructs: `/api/assets/screenshots/session/capture-123.png`
   - ✅ This path is **public** (no API key required)

---

## Example n8n "Set" Node Configuration

If you're using a **Set** node to build the callback body:

**Field Mappings:**
```
filename → Expression: {{ $('Webhook').item.json.input_data.screenshot_key }}
rawColors → Expression: {{ $json.rawColors }}
colourData → Expression: {{ $json.colourData }}
emotionPrediction → Expression: { "all_intensities": {{ $json.all_intensities }} }
```

---

## Alternative: Using Function Node

```javascript
// In your Function node that builds the callback body:

const inputData = items[0].json.input_data || {};
const screenshotKey = inputData.screenshot_key || '';

return {
  json: {
    success: true,
    result_data: {
      filename: screenshotKey,  // ← Full R2 key with path
      rawColors: items[0].json.rawColors,
      colourData: items[0].json.colourData,
      emotionPrediction: {
        all_intensities: items[0].json.all_intensities
      }
    }
  }
};
```

---

## Testing the Fix

### Test Data

Use this in n8n to test your callback:

```json
{
  "input_data": {
    "screenshot_key": "screenshots/test-session/capture-1234567890.png"
  },
  "rawColors": {
    "#ff0000": 0.5,
    "#00ff00": 0.5
  },
  "colourData": {
    "red": 0.5,
    "green": 0.5
  },
  "all_intensities": {
    "happiness": "high",
    "love": "medium",
    "optimism": "low",
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
```

### Expected Callback Output

```json
{
  "success": true,
  "result_data": {
    "filename": "screenshots/test-session/capture-1234567890.png",
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
        ...
      }
    }
  }
}
```

---

## Troubleshooting

### Issue 1: Still Getting 401

**Symptom:** Image URL is `/api/uploads/...`

**Cause:** n8n is still sending basename only

**Fix:** Ensure `filename` field uses full `screenshot_key` from input

### Issue 2: Image 404 Not Found

**Symptom:** Image URL is correct but returns 404

**Cause:** R2 file doesn't exist or path is wrong

**Fix:** Check R2 bucket to verify the file was uploaded correctly

### Issue 3: n8n Can't Access screenshot_key

**Symptom:** `filename` is empty or undefined

**Cause:** Wrong reference path in n8n

**Fix:** Use `{{ $('Webhook').item.json.input_data.screenshot_key }}` or check your webhook node name

---

## Summary

**One Line Fix:**

In your n8n callback body, change:
```javascript
filename: "capture-123.png"  // ❌ Wrong
```

To:
```javascript
filename: items[0].json.input_data.screenshot_key  // ✅ Correct
```

This passes the full R2 path (`screenshots/session/capture-123.png`) so the frontend can construct the public URL (`/api/assets/screenshots/session/capture-123.png`).

**No Cloudflare changes needed** - the API is already configured correctly!

---

**Related Files:**
- `memory/N8N_PALETTE_ANALYSIS_RESPONSE.md` - Updated response schema
- `apps/frontend/functions/api/uploads/screenshot.ts` - Upload endpoint (already correct)
- `apps/frontend/functions/api/assets/[[path]].ts` - Public asset serving (already correct)
- `apps/frontend/src/views/ColorPalettePage.vue` - Frontend display (already correct)

**Status:** ✅ Ready to Apply - Update n8n workflow only!
