# API Security Measures

This document outlines the security measures implemented to ensure your OpenAI API key is **ONLY** used for story generation.

## 🔒 Security Features Implemented

### 1. **Lazy Initialization**
- The OpenAI API client is **NOT** initialized when the StoryGenerator class is created
- It's only initialized when an actual story generation request is made
- This prevents any accidental API usage during setup or testing

### 2. **Request Validation**
The `SecureStoryGenerator` validates all requests before any API call:
- ✅ Must have exactly 3 paintings
- ✅ Each painting must have title, artist, and year
- ✅ Narrative style must be one of: historian, poet, detective, critic, time_traveller
- ❌ Invalid requests are rejected without touching the API

### 3. **API Call Logging**
Every API interaction is logged with:
- Timestamp of the request
- Narrative style requested
- Paintings selected
- Success/failure status
- Word count of generated story

### 4. **Single Purpose Design**
- The API is **ONLY** called in one place: `story_generator.py` line ~115
- The API is **ONLY** used for story generation
- No other operations can trigger API calls

### 5. **Usage Tracking**
- Total API calls are counted
- Detailed log of each call is maintained
- Session summary shows total API usage

## 📊 Monitoring API Usage

### Check API Usage Stats
```python
generator = StoryGenerator()
stats = generator.get_api_usage_stats()
print(f"Total API calls: {stats['total_api_calls']}")
```

### View API Call Log
The `api_usage_log.json` file tracks all API requests with full details.

### Console Logging
All API calls are logged to console with `[API]` prefix:
```
[API] OpenAI client initialized for story generation
[API] Making story generation call #1
[API] Style: historian
[API] Paintings: The Starry Night by Vincent Van Gogh, ...
[API] Story generated successfully (327 words)
```

## 🚫 What the API CANNOT Do

Your API key **CANNOT** be used for:
- ❌ General chat or conversations
- ❌ Code generation
- ❌ Text analysis
- ❌ Translation
- ❌ Any purpose other than story generation

## ✅ What the API CAN Do

Your API key can **ONLY** be used for:
- ✅ Generating 300-word stories based on 3 paintings
- ✅ Using one of 5 predefined narrative styles
- ✅ Through validated requests only

## 🛡️ Server Integration

The server uses `secure_story_generator.py` which adds an extra layer of validation and logging before any API call.

## 📝 Testing

Run the security test to verify all restrictions are working:
```bash
python3 test_api_restrictions.py
```

This will verify:
1. API client lazy initialization
2. Invalid request rejection
3. Proper API call logging
4. Single-purpose usage

## 🔑 Your API Key

Your API key is stored in `.env` and is:
- Only loaded when needed
- Only used for story generation
- Never exposed in logs or error messages
- Protected by multiple validation layers 