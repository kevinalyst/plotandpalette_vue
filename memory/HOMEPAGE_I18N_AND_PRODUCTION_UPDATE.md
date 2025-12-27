# Homepage I18n Hero Text & Production Update

**Date:** December 27, 2025  
**Status:** ✅ Complete  
**Deployment:** https://1efbd1f3.plotandpalette-vue-local.pages.dev

## Overview
Converted the homepage background image text to translatable HTML elements, added custom font support with language-specific styling, switched to production n8n webhook, added error handling, and cleaned up UI by hiding non-essential buttons.

---

## 1. Homepage Hero Text Internationalization

### Problem
The homepage used a static background image (`backgroundtext.png`) containing:
- Title: "Plot & Palette" - Uegor Regular - 160pt
- Subtitle: "Every palette tells a story. Discover yours." - Poppins Medium - 38pt
- Description: Full paragraph text - Poppins Regular - 20pt

This text couldn't be translated for the Chinese version.

### Solution
Replaced the background image with translatable HTML text elements.

**Files Modified:**
- `apps/frontend/src/locales/en.json` - Added `home.heroTitle`, `home.heroSubtitle`, `home.heroDescription`
- `apps/frontend/src/locales/zh.json` - Added Chinese translations
- `apps/frontend/src/views/HomePage.vue` - Added text elements and styling

**Template Changes:**
```vue
<div class="text-container">
  <h1 class="hero-title" :class="{ 'hero-title-zh': $i18n.locale === 'zh' }">
    {{ $t('home.heroTitle') }}
  </h1>
  <h2 class="hero-subtitle" :class="{ 'hero-subtitle-zh': $i18n.locale === 'zh' }">
    {{ $t('home.heroSubtitle') }}
  </h2>
  <p class="hero-description" :class="{ 'hero-description-zh': $i18n.locale === 'zh' }">
    {{ $t('home.heroDescription') }}
  </p>
</div>
```

**CSS Styling:**
- Left-aligned layout (not centered)
- Fixed positioning: `left: 160px`, `top: 40%`
- Font sizes: 120px (title), 26px (subtitle), 16px (description)

---

## 2. Custom Font Integration

### Uegor Regular Font
**File Added:** `apps/frontend/src/assets/images/Uegor-Regular.otf`

**Font-Face Declaration in HomePage.vue:**
```css
@font-face {
  font-family: 'Uegor Regular';
  src: url('~@/assets/images/Uegor-Regular.otf') format('opentype');
  font-weight: normal;
  font-style: normal;
}
```

**Applied to:**
```css
.hero-title {
  font-family: 'Uegor Regular', 'Georgia', 'Times New Roman', serif;
  font-size: 120px;
}
```

---

## 3. Language-Specific Styling

### Chinese Typography Override
Added dedicated CSS classes for Chinese language that automatically apply when language is switched to Chinese (`$i18n.locale === 'zh'`).

**CSS Classes:**
```css
.hero-title-zh {
  font-family: 'PingFang SC', 'Noto Sans SC', 'Microsoft YaHei', 'SimHei', sans-serif;
  font-size: 80px;
  letter-spacing: 0.05em;
}

.hero-subtitle-zh {
  font-family: 'PingFang SC', 'Noto Sans SC', 'Microsoft YaHei', sans-serif;
  font-size: 26px;
}

.hero-description-zh {
  font-family: 'PingFang SC', 'Noto Sans SC', 'Microsoft YaHei', sans-serif;
  font-size: 16px;
  line-height: 1.8;
}
```

**How to customize:**
To change Chinese text appearance, simply edit these `-zh` classes in `apps/frontend/src/views/HomePage.vue`.

---

## 4. Production Webhook Update

### Changed n8n Endpoint
**File:** `apps/frontend/wrangler.toml`

**Before:**
```toml
N8N_WEBHOOK_URL = "https://kevinalyst.app.n8n.cloud/webhook-test/97dac6bc-5ecc-42f2-89f8-d0c4e883c38d"
```

**After:**
```toml
N8N_WEBHOOK_URL = "https://kevinalyst.app.n8n.cloud/webhook/97dac6bc-5ecc-42f2-89f8-d0c4e883c38d"
```

Now using the production n8n webhook endpoint (removed `-test` suffix).

---

## 5. Error Handling Improvements

### GradientPalette.vue Safety Check
Added validation to prevent passing `undefined` data to ColorPalettePage.

**Problem:**
When job completed but `result_data` was undefined, the code would:
- Stringify undefined → `"undefined"`
- Base64 encode → pass to ColorPalettePage
- ColorPalettePage tries to parse → `SyntaxError: "undefined" is not valid JSON`

**Fix Added:**
```javascript
if (status === 'COMPLETED') {
  const result = statusResponse.data.result_data
  
  // SAFETY CHECK: Ensure result_data exists before navigation
  if (!result) {
    console.error('❌ Job completed but result_data is missing!', {
      statusResponse: statusResponse,
      jobData: statusResponse.data,
      hasResultData: 'result_data' in statusResponse.data,
      resultDataValue: statusResponse.data.result_data
    })
    throw new Error('Job completed but result_data is missing from API response.')
  }
  
  // Continue with navigation...
}
```

This provides detailed logging to diagnose the root cause if the issue persists.

---

## 6. UI Cleanup - Hidden Buttons

### Buttons Hidden
Added `v-if="false"` to hide non-essential UI elements:

**HomePage.vue:**
1. Logo refresh button (top left corner)
2. "Get in touch" button (top right)
3. "People" button (top right)

**StoryPage.vue:**
4. "Leave us feedback" button (action buttons area)

**Why v-if="false"?**
- Completely removes from DOM (no rendering overhead)
- Easy to re-enable by changing to `v-if="true"`
- Preserves all code and styling for future use

---

## 7. Removed References

### Deleted paintingsguide.png
**File Deleted:** `apps/frontend/src/assets/images/paintingsguide.png`

**Removed References From:**
- `apps/frontend/src/views/HomePage.vue` - Deleted hover effect CSS using paintingsguide.png
- `apps/frontend/src/style.css` - Deleted paintings-container hover effect

This prevented module not found errors during build.

---

## Translation Keys Added

### English (en.json)
```json
"home": {
  "heroTitle": "Plot & Palette",
  "heroSubtitle": "Every palette tells a story. Discover yours.",
  "heroDescription": "With Plot & Palette, unlock the stories behind the canvas..."
}
```

### Chinese (zh.json)
```json
"home": {
  "heroTitle": "情节与调色板",
  "heroSubtitle": "每个调色板都讲述一个故事。发现你的故事。",
  "heroDescription": "借助情节与调色板，解锁画布背后的故事..."
}
```

---

## Deployment History

**Latest:** https://1efbd1f3.plotandpalette-vue-local.pages.dev  
**Previous:** https://69d03967.plotandpalette-vue-local.pages.dev  
**Project:** plotandpalette-vue-local  

---

## Files Changed Summary

**Modified (13 files):**
1. `apps/frontend/src/locales/en.json` - Hero text keys
2. `apps/frontend/src/locales/zh.json` - Chinese translations
3. `apps/frontend/src/views/HomePage.vue` - Hero text, fonts, hidden buttons
4. `apps/frontend/src/views/StoryPage.vue` - Hidden feedback button
5. `apps/frontend/src/views/GradientPalette.vue` - Error handling
6. `apps/frontend/src/style.css` - Removed paintingsguide reference
7. `apps/frontend/wrangler.toml` - Production webhook URL
8. `apps/frontend/src/assets/images/dance.gif` - Binary update
9. `apps/frontend/src/assets/images/keyboard.gif` - Binary update
10. `apps/frontend/src/assets/images/magiccube.gif` - Binary update
11. `apps/frontend/src/assets/images/paintings.png` - Binary update
12. `apps/frontend/src/views/ColorPalettePage.vue` - Minor updates

**Added (1 file):**
- `apps/frontend/src/assets/images/Uegor-Regular.otf` - Custom font

**Deleted (1 file):**
- `apps/frontend/src/assets/images/paintingsguide.png` - No longer used

---

## Testing Notes

### To Test Homepage
1. Visit: https://1efbd1f3.plotandpalette-vue-local.pages.dev
2. Check that hero text displays on the left side
3. Toggle language switcher between EN and 中文
4. Verify English uses Uegor Regular font (120px)
5. Verify Chinese uses PingFang SC font (80px)
6. Confirm logo, get-in-touch, and people buttons are hidden

### To Test Story Page
1. Complete a full user journey to reach StoryPage
2. Confirm "Leave us feedback" button is hidden
3. Only 3 buttons should appear: Download, Re-generate, Re-capture

---

## Future Maintenance

### To Re-enable Hidden Buttons
Change `v-if="false"` to `v-if="true"` in:
- HomePage.vue (3 buttons)
- StoryPage.vue (1 button)

### To Customize Chinese Text Styling
Edit the `-zh` CSS classes in `apps/frontend/src/views/HomePage.vue`:
- `.hero-title-zh` - Title styling
- `.hero-subtitle-zh` - Subtitle styling  
- `.hero-description-zh` - Description styling

### To Edit Translations
Modify:
- `apps/frontend/src/locales/en.json` - English text
- `apps/frontend/src/locales/zh.json` - Chinese text
