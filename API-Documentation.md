# Plot & Palette API Documentation

## Backend and Story API Data Flow

This section documents the current backend pipelines and the Story API integration, including exactly where data is persisted to the database.

### Backend (Flask)

#### Key Endpoints
- POST `/capture-palette`: capture frame or receive palette image, run Emotion Prediction + Painting Recommendation, persist metadata, return results
- POST `/get-recommendations`: run combined pipeline from a saved filename (image must exist on server filesystem)
- POST `/get-recommendations-from-colors`: run recommendation only using raw color stats
- POST `/save-emotion`: persist the emotion the user picked
- POST `/save-selection`: persist selected paintings and narrative style
- GET `/session-palette/<session_id>`: fetch recent palette metadata (used for resume flows)

#### Emotion Prediction Pipeline
1. Save uploaded image to `uploads/`.
2. Execute `emotions_generation/emotion_prediction.py` with the image path.
3. Parse stdout to extract:
   - `colourData` (basic color percentages)
   - `rawColors` (list of 5 weighted colors for recommender)
   - `rawColorsForFrontend` (hex→percentage map)
   - `emotionPrediction` (dominant emotion, confidence, per-emotion probabilities)
4. Persist and return:
   - Write metadata JSON next to the image in `uploads/<filename>.json` with color stats, raw colors, emotion, and initial recommendations.
   - If DB enabled: store probabilities via `db.save_palette_analyse(session_id, gifname, emotion_scores)`.

Code references:

```730:980:server.py
# /capture-palette: save frame/image → run run_python_script → emotion → recommendation
```

```243:327:server.py
def parse_emotion_prediction_output(output): ...
```

#### Painting Recommendation Pipeline
1. Input: five raw colors with percentages.
2. Execute `painting_recommendation/recommendation_service.py`:
   - compute color stats, cluster mapping and candidate pool `N_CAND=600`
   - penalties, cooldown, softmax sampling `N_SAMPLE=60`
   - MMR re-ranking `K_FINAL=12`
   - cluster quotas `QUOTA_MAX=0.6`
   - produce `final_recommendations` (urls, page, artist, title, cluster_id, filename, similarity)
3. Backend parses script stdout into `urls` and `detailedRecommendations` and returns them.
4. If called from `/capture-palette`, DB persist first 10 URLS via `db.save_painting_recommendations(session_id, urls)`.

Code references:

```1340:1377:server.py
/get-recommendations-from-colors: accepts rawColors (5), runs run_recommendation_service
```

```600:741:painting_recommendation/recommendation_service.py
apply quotas, slice to NUM_RECOMMENDATIONS, print detailed JSON
```

```329:397:server.py
def parse_recommendation_service_output(output): extracts urls + detailedRecommendations
```

#### Database Persistence Points (Backend)
- Palette upload (legacy upload route):
  - `db.create_or_get_user(session_id, user_agent, ip_address)`
  - `db.save_palette(filename, original_name, colors, file_size, session_id, metadata)`
  - Ref: `server.py` 1000–1065
- Emotion prediction save (from `/capture-palette`):
  - `db.save_palette_analyse(session_id, gifname, emotion_scores)`
  - Ref: `server.py` ~912
- Painting recommendations (from `/capture-palette`):
  - `db.save_painting_recommendations(session_id, urls)`
  - Ref: `server.py` ~933
- Emotion selection (Step 2):
  - `db.save_emotion_selection(session_id, selected_emotion, probability)`
  - Ref: `server.py` 1474–1484
- Selection (Step 3):
  - `db.save_paintings_style(session_id, painting_urls, story_character, nickname)`
  - Ref: `server.py` 1416–1428
- Feedback form:
  - `db.save_feedback_form(...)` (Ref near ~1775)

### Story API (Flask)

#### Endpoints
- GET `/health`: health check
- POST `/test-files`: verify `imagePath` files exist inside the container
- POST `/generate`: generate story content (strict validation + logging)

#### Flow
1. Backend/Frontend posts to `/generate` with:
   - `paintings` (3 objects: title, artist, year, imagePath)
   - `character` (historian|poet|detective|critic|time_traveller)
   - optional `nickname`, `emotion`, `emotion_probability`
2. Story API spawns `secure_story_generator.py` with JSON payload.
3. Secure generator validates payload, logs API usage to `story_generation/api_usage_log.json`, and delegates to `ImageStoryGenerator` (Claude-backed) to produce the story.
4. Returns JSON with the generated story.

Code references:

```45:93:story_generation/story_api.py
/generate → run secure_story_generator.py; return its JSON stdout
```

```21:61, 93:129, 130:168:story_generation/secure_story_generator.py
Validate request, log usage, generate story, return JSON
```

#### Persistence (Story API)
- Usage/activity logging to `story_generation/api_usage_log.json` (file-based; not DB)
- Backend persists selection/emotion/metadata via its own endpoints as listed above

### Dev vs Prod Notes
- In dev (localhost:8080), use `/api/get-recommendations-from-colors` for Reload to re-sample recommendations with the same color stats; filename-based `/get-recommendations` expects built static paths.
- Diversity quota is `QUOTA_MAX=0.6`. If the quota reduces below 10, results can be <10. Backfilling is not implemented yet.

This document provides comprehensive documentation for all API endpoints in the Plot & Palette application.

## Architecture Overview

The application uses a microservices architecture with:
- **Main Backend Service** (Flask) - Port 5003 (externally 5003)
- **Emotion Prediction API** (FastAPI) - Port 5001
- **Story Generation API** (Flask) - Port 5002
- **Frontend** (Vue.js + Vite) - Port 8080 (dev) / 8081 (container)
- **Nginx Reverse Proxy** - Port 80/443
- **MySQL Database** - 7 normalized tables for clean data separation

---

## Main Backend API Endpoints
**Base URL**: `http://localhost:5003/api` (accessed via nginx as `/api`)

### Health & Status

#### GET `/health`
**Description**: Health check endpoint
**Request**: None
**Response**:
```json
{
  "status": "healthy",
  "message": "Plot & Palette API is running",
  "timestamp": "2024-07-25T10:30:00Z"
}
```

#### GET `/status`
**Description**: Service status endpoint
**Request**: None
**Response**:
```json
{
  "status": "running",
  "services": {
    "database": true,
    "emotion_api": true,
    "story_api": true
  }
}
```

### Session Management

#### POST `/store-username`
**Description**: Store username and user demographics in the `user_info` table (without creating session)
**Request**:
```json
{
  "name": "John Doe",
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
  "username": "John Doe",
  "message": "Username stored successfully"
}
```
**Database Impact**: Creates/updates record in `user_info` table with username as primary identifier

#### POST `/create-session`
**Description**: Create a new session linked to existing username in the `user_session` table
**Request**:
```json
{
  "username": "John Doe"
}
```
**Response**:
```json
{
  "success": true,
  "sessionId": "a0c80fd5-bd9f-469b-8dd8-1227a7175b0a",
  "username": "John Doe",
  "message": "Session created successfully"
}
```
**Database Impact**: Creates record in `user_session` table linking username to new session_id

### Palette Capture & Analysis

#### POST `/capture-gif-frame` 
**Description**: Capture a specific frame from a GIF file
**Request**:
```json
{
  "gifName": "5.gif",
  "frameIndex": 10,
  "sessionId": "session-id"
}
```
**Response**:
```json
{
  "success": true,
  "filename": "captured_frame_1627234567.jpg",
  "message": "Frame captured successfully"
}
```

#### POST `/capture-palette`
**Description**: Capture and analyze palette from GIF frame with emotion prediction and recommendations
**Request**:
```json
{
  "gifName": "5.gif",
  "frameData": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ...",
  "sessionId": "session-id"
}
```
**Response**:
```json
{
  "success": true,
  "filename": "palette_20240725_103045.jpg",
  "colourData": {
    "red": 0.25,
    "blue": 0.35,
    "yellow": 0.15,
    "green": 0.10,
    "orange": 0.15
  },
  "rawColors": [
    {"r": 255, "g": 100, "b": 50, "percentage": 0.25},
    {"r": 50, "g": 150, "b": 255, "percentage": 0.35}
  ],
  "emotionPrediction": {
    "dominant_emotion": "happiness",
    "confidence": 0.85,
    "all_probabilities": {
      "happiness": 0.85,
      "trust": 0.72,
      "optimism": 0.68,
      "anticipation": 0.45
    }
  },
  "recommendations": ["https://example.com/painting1.jpg"],
  "detailedRecommendations": [
    {
      "title": "Starry Night",
      "artist": "Vincent van Gogh",
      "year": "1889",
      "url": "https://example.com/starry-night.jpg"
    }
  ]
}
```
**Database Impact**: 
- Saves emotion analysis results to `palette_analyse` table (15 emotion scores + gifname)
- Saves recommended painting URLs to `painting_recommendations` table (up to 10 URLs)

#### POST `/save-palette`
**Description**: Save palette image (FormData upload)
**Request**: FormData with image file
**Response**:
```json
{
  "success": true,
  "filename": "uploaded_palette.jpg",
  "message": "Palette saved successfully"
}
```

#### GET `/palette/<filename>`
**Description**: Get palette information by filename
**Request**: None (filename in URL)
**Response**:
```json
{
  "filename": "palette_123.jpg",
  "colourData": {...},
  "timestamp": "2024-07-25T10:30:00Z"
}
```

#### GET `/recent-palettes`
**Description**: Get list of recently captured palettes
**Request**: None
**Response**:
```json
{
  "palettes": [
    {
      "filename": "palette_123.jpg",
      "timestamp": "2024-07-25T10:30:00Z",
      "colourData": {...}
    }
  ]
}
```

### Recommendations

#### POST `/get-recommendations`
**Description**: Get painting recommendations based on color analysis
**Request**:
```json
{
  "colourData": {
    "red": 0.25,
    "blue": 0.35,
    "yellow": 0.15
  },
  "sessionId": "session-id"
}
```
**Response**:
```json
{
  "success": true,
  "recommendations": ["https://example.com/painting1.jpg"],
  "detailedRecommendations": [
    {
      "title": "The Scream",
      "artist": "Edvard Munch", 
      "year": "1893",
      "url": "https://example.com/scream.jpg"
    }
  ]
}
```

### Emotion & Selection Management

#### POST `/save-emotion`
**Description**: Save user's selected emotion choice
**Request**:
```json
{
  "emotion": "happiness",
  "probability": 0.85,
  "sessionId": "session-id"
}
```
**Response**:
```json
{
  "success": true,
  "message": "Emotion saved successfully"
}
```
**Database Impact**: Creates/updates record in `emotion_selection` table with user's chosen emotion

#### POST `/save-selection`
**Description**: Save user's painting selections and character choice for story generation
**Request**:
```json
{
  "selectedPaintings": [
    {
      "title": "Starry Night",
      "artist": "Vincent van Gogh",
      "year": "1889",
      "url": "https://example.com/starry-night.jpg"
    }
  ],
  "character": "poet",
  "nickname": "Alex",
  "sessionId": "session-id"
}
```
**Response**:
```json
{
  "success": true,
  "message": "Selection saved successfully"
}
```
**Database Impact**: Creates/updates record in `paintings_style` table with 3 selected painting URLs, story character, and nickname

#### GET `/selection-history`
**Description**: Get user's selection history
**Request**: None
**Response**:
```json
{
  "selections": [
    {
      "timestamp": "2024-07-25T10:30:00Z",
      "paintings": [...],
      "character": "poet",
      "emotion": "happiness"
    }
  ]
}
```

### Story Generation

#### POST `/generate-story`
**Description**: Generate AI story based on selected paintings and character
**Request**:
```json
{
  "paintings": [
    {
      "title": "Starry Night",
      "artist": "Vincent van Gogh", 
      "year": "1889",
      "url": "https://example.com/starry-night.jpg"
    }
  ],
  "character": "poet",
  "userName": "Alex",
  "sessionId": "session-id"
}
```
**Response**:
```json
{
  "success": true,
  "story": {
    "story_text": "In the swirling night sky above Saint-Rémy...",
    "story_title": "Whispers in Starlit Dreams",
    "narrative_style": "poet",
    "user_name": "Alex",
    "paintings_used": [...]
  }
}
```

### Feedback

#### POST `/submit-feedback`
**Description**: Submit comprehensive user feedback survey with Q1-Q15 responses
**Request**:
```json
{
  "answers": {
    "q1": 4,
    "q2": 5,
    "q3": 3,
    "q4": 4,
    "q5": 5,
    "q6": 4,
    "q7": 5,
    "q8": 4,
    "q9": 5,
    "q10": 4,
    "q11": 5,
    "q12": 4,
    "q13": 5,
    "q14": "I loved the color palette analysis and emotion prediction features!",
    "q15": "Maybe add more painting styles in the recommendations."
  },
  "sessionId": "session-id"
}
```
**Response**:
```json
{
  "success": true,
  "message": "Feedback submitted successfully"
}
```
**Database Impact**: Creates/updates record in `feedback_form` table with Q1-Q13 as integers (1-5 ratings) and Q14-Q15 as text responses

### File Serving

#### GET `/uploads/<filename>`
**Description**: Serve uploaded files
**Request**: None (filename in URL)
**Response**: File content

#### GET `/favicon.ico`
**Description**: Serve favicon
**Request**: None
**Response**: Favicon file

#### GET `/`
**Description**: Serve main application
**Request**: None
**Response**: HTML content

---

## Emotion Prediction API Endpoints
**Base URL**: `http://localhost:5001` (internal microservice)

### Core Prediction

#### POST `/predict`
**Description**: Predict emotions from color features
**Request**:
```json
{
  "colors": {
    "red": 0.25,
    "blue": 0.35,
    "green": 0.10,
    "yellow": 0.15,
    "orange": 0.15,
    "purple": 0.0,
    "pink": 0.0,
    "brown": 0.0,
    "black": 0.0,
    "white": 0.0,
    "grey": 0.0,
    "turquoise": 0.0
  },
  "engineered_features": null
}
```
**Response**:
```json
{
  "dominant_emotion": "happiness",
  "confidence": 0.85,
  "all_probabilities": {
    "happiness": 0.85,
    "trust": 0.72,
    "optimism": 0.68,
    "anticipation": 0.45,
    "anger": 0.12,
    "fear": 0.08,
    "sadness": 0.05
  },
  "prediction_metadata": {
    "model_version": "v1.0",
    "timestamp": "2024-07-25T10:30:00Z"
  }
}
```

### Health & Info

#### GET `/health`
**Description**: Health check for emotion prediction service
**Request**: None
**Response**:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "timestamp": "2024-07-25T10:30:00Z",
  "model_info": {
    "model_type": "GradientBoostingClassifier with MultiOutputClassifier",
    "final_auc": "0.85",
    "features_used": "85",
    "emotions_predicted": "15"
  }
}
```

**Supported Emotions**: The API predicts probabilities for 15 emotions:
- `anger`, `anticipation`, `arrogance`, `disagreeableness`, `disgust`
- `fear`, `gratitude`, `happiness`, `humility`, `love`
- `optimism`, `pessimism`, `sadness`, `surprise`, `trust`

#### GET `/model-info`
**Description**: Get detailed model information
**Request**: None
**Response**:
```json
{
  "model_type": "GradientBoostingClassifier with MultiOutputClassifier",
  "final_auc": 0.85,
  "features_used": 85,
  "color_features": ["red", "blue", "green", "yellow", "orange", "purple", "pink", "brown", "black", "white", "grey", "turquoise"],
  "emotion_classes": ["anger", "anticipation", "arrogance", "disagreeableness", "disgust", "fear", "gratitude", "happiness", "humility", "love", "optimism", "pessimism", "sadness", "surprise", "trust"],
  "training_date": "2024-06-15"
}
```

#### GET `/`
**Description**: Service root endpoint
**Request**: None
**Response**:
```json
{
  "service": "emotion-prediction-api",
  "version": "1.0.0",
  "status": "running"
}
```

---

## Story Generation API Endpoints
**Base URL**: `http://localhost:5002` (internal microservice)

### Story Creation

#### POST `/generate`
**Description**: Generate AI-powered story from paintings and character selection
**Request**:
```json
{
  "paintings": [
    {
      "title": "Starry Night",
      "artist": "Vincent van Gogh",
      "year": "1889", 
      "url": "https://example.com/starry-night.jpg",
      "imagePath": "/app/uploads/starry_night.jpg"
    },
    {
      "title": "The Scream",
      "artist": "Edvard Munch",
      "year": "1893",
      "url": "https://example.com/scream.jpg", 
      "imagePath": "/app/uploads/scream.jpg"
    },
    {
      "title": "Girl with a Pearl Earring",
      "artist": "Johannes Vermeer",
      "year": "1665",
      "url": "https://example.com/pearl_earring.jpg",
      "imagePath": "/app/uploads/pearl_earring.jpg"
    }
  ],
  "character": "poet",
  "userName": "Alex",
  "narrative_style": "poet"
}
```
**Response**:
```json
{
  "success": true,
  "story_text": "In the swirling depths of a starlit night, Alex wandered through galleries of dreams...",
  "story_title": "Whispers in Starlit Dreams",
  "narrative_style": "poet",
  "user_name": "Alex", 
  "paintings_used": [
    {
      "title": "Starry Night",
      "artist": "Vincent van Gogh",
      "year": "1889"
    }
  ],
  "api_calls_used": 2,
  "generation_timestamp": "2024-07-25T10:30:00Z"
}
```

### Health & Testing

#### GET `/health`
**Description**: Health check for story generation service
**Request**: None
**Response**:
```json
{
  "status": "healthy",
  "service": "story-generation"
}
```

#### POST `/test-files`
**Description**: Test accessibility of uploaded painting files
**Request**:
```json
{
  "paintings": [
    {
      "imagePath": "/app/uploads/painting1.jpg"
    },
    {
      "imagePath": "/app/uploads/painting2.jpg"
    }
  ]
}
```
**Response**:
```json
{
  "success": true,
  "file_status": [
    {
      "index": 0,
      "path": "/app/uploads/painting1.jpg",
      "exists": true,
      "size": 245760
    },
    {
      "index": 1,
      "path": "/app/uploads/painting2.jpg", 
      "exists": false,
      "size": 0
    }
  ],
  "uploads_dir_exists": true,
  "uploads_contents": ["painting1.jpg", "palette_123.jpg"]
}
```

---

## Frontend API Service Usage

The frontend uses a centralized `ApiService` class located in `frontend-vue/src/services/api.js` that provides the following methods:

### Main Methods
- `checkHealth()` - Calls `/health`
- `getStatus()` - Calls `/status`
- `savePalette(formData)` - Calls `/save-palette`
- `getRecommendations(data)` - Calls `/get-recommendations`
- `getPaletteInfo(filename)` - Calls `/palette/${filename}`
- `getRecentPalettes()` - Calls `/recent-palettes`
- `saveEmotion(data)` - Calls `/save-emotion`
- `saveSelection(data)` - Calls `/save-selection`
- `getSelectionHistory()` - Calls `/selection-history`
- `generateStory(data)` - Calls `/generate-story`

### Usage Example
```javascript
import ApiService from '@/services/api.js'

// Create session
const session = await ApiService.request('/create-username', {
  method: 'POST',
  body: JSON.stringify({
    name: 'John Doe',
    age: '25-34',
    gender: 'man'
  })
})

// Generate story
const story = await ApiService.generateStory({
  paintings: selectedPaintings,
  character: 'poet',
  userName: 'John'
})
```

---

## Error Handling

All endpoints return consistent error responses:

### Error Response Format
```json
{
  "error": "Error type description",
  "message": "Detailed error message",
  "timestamp": "2024-07-25T10:30:00Z"
}
```

### Common HTTP Status Codes
- `200 OK` - Successful request
- `400 Bad Request` - Invalid request data
- `404 Not Found` - Resource not found
- `413 Payload Too Large` - File too large
- `500 Internal Server Error` - Server error

---

## Authentication & Security

- **Session Management**: All endpoints accept `sessionId` parameter
- **CORS**: Enabled for cross-origin requests
- **File Upload Security**: Filenames are sanitized using `secure_filename()`
- **Rate Limiting**: Not currently implemented
- **API Keys**: Used for external services (Claude AI, etc.)

---

## Development & Production URLs

### Development (Vite Dev Server)
- Frontend: `http://localhost:8080`
- API Proxy: `http://localhost:8080/api` → `http://localhost:5003`

### Production (Nginx)
- Frontend: `http://localhost` 
- API: `http://localhost/api` → `http://backend:5000` (internal)

### Internal Microservices
- Backend: `http://backend:5000` (internal) / `http://localhost:5003` (external)
- Emotion API: `http://emotion-api:5001`
- Story API: `http://story-api:5002`

---

## Database Schema

The application uses a **7-table normalized MySQL database**:

### Core Tables (No ID Columns - Natural Keys as Primary Keys)
1. **`user_info`** - User demographics (username PRIMARY KEY, age, gender, fieldOfStudy, frequency)
2. **`user_session`** - Session management (session_id PRIMARY KEY, username FK)
3. **`palette_analyse`** - Emotion analysis results (session_id PRIMARY KEY, 15 emotion probabilities + gifname)
4. **`painting_recommendations`** - Recommended URLs (session_id PRIMARY KEY, 10 painting URLs)
5. **`emotion_selection`** - User's emotion choice (session_id PRIMARY KEY, selected_emotion)
6. **`paintings_style`** - Selected paintings for story (session_id PRIMARY KEY, 3 URLs + character + nickname)
7. **`feedback_form`** - User feedback and survey (session_id PRIMARY KEY, Q1-Q15 structured responses)

### Data Flow
```
/store-username → user_info
/create-session → user_session
/capture-palette → palette_analyse + painting_recommendations
/save-emotion → emotion_selection
/save-selection → paintings_style
/submit-feedback → feedback_form
```

### Foreign Key Relationships
- `user_session.username` → `user_info.username` (FK)
- All other tables use `session_id` as PRIMARY KEY → `user_session.session_id` (FK)
- **Cascade deletes** ensure data consistency
- **One-to-One guarantees**: Each session can only have one record per table

## Total Endpoint Count

**Main Backend API**: 16 endpoints
**Emotion Prediction API**: 4 endpoints  
**Story Generation API**: 3 endpoints

**Total**: 23 API endpoints 