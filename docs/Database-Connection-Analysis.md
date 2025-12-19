# Database Connection Analysis: Server-Database Data Types & Formats

This document analyzes the data types and formats expected by the database versus what the server actually sends.

## Database Schema Overview

The application uses **MySQL 8.0** with **7 main tables**:
1. **`user_info`** (5 columns) - User demographics and profile information
2. **`user_session`** (2 columns) - Session management linking users to sessions
3. **`palette_analyse`** (16 columns) - Emotion analysis results from palette capture
4. **`painting_recommendations`** (10 columns) - Recommended painting URLs from analysis
5. **`emotion_selection`** (1 column) - User's selected emotion choice
6. **`paintings_style`** (5 columns) - User's selected paintings and character for story
7. **`feedback_form`** (15 columns) - User feedback and survey responses

---

## Table 1: `user_info` (User Demographics)

### Database Expected Format

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| `username` | `VARCHAR(255)` | `PRIMARY KEY` | User's display name (primary identifier) |
| `age` | `VARCHAR(255)` | `NULL` | Age range or specific age as string |
| `gender` | `VARCHAR(255)` | `NULL` | Gender identity |
| `fieldOfStudy` | `VARCHAR(255)` | `NULL` | Field of study or profession |
| `frequency` | `VARCHAR(255)` | `NULL` | Art engagement frequency |
| `created_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP` | Auto-generated |
| `updated_at` | `TIMESTAMP` | `ON UPDATE CURRENT_TIMESTAMP` | Auto-managed |

### Server Data Being Sent

**From `/store-username` endpoint:**
```python
db.save_user_info(
    username=username,                    # String (user's name)
    age=age,                             # String (age range like "25-34")
    gender=gender,                       # String
    fieldOfStudy=fieldOfStudy,          # String
    frequency=frequency                  # String
)
```

### ✅ Compatibility Analysis
- **Username**: ✅ Compatible - String fits VARCHAR(255) and serves as unique identifier
- **Age**: ✅ Compatible - Now stored as VARCHAR to handle age ranges like "25-34"
- **Gender**: ✅ Compatible - String fits VARCHAR(255)
- **FieldOfStudy**: ✅ Compatible - String fits VARCHAR(255)
- **Frequency**: ✅ Compatible - String fits VARCHAR(255)

---

## Table 2: `user_session` (Session Management)

### Database Expected Format

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| `session_id` | `VARCHAR(255)` | `PRIMARY KEY` | UUID session identifier |
| `username` | `VARCHAR(255)` | `NOT NULL` | Foreign key to user_info.username |
| `created_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP` | Auto-generated |
| `updated_at` | `TIMESTAMP` | `ON UPDATE CURRENT_TIMESTAMP` | Auto-managed |

### Server Data Being Sent

**From `/create-session` endpoint:**
```python
db.create_session(
    username=username,          # String (user's name)
    session_id=session_id       # String (UUID)
)
```

### ✅ Compatibility Analysis
- **Username**: ✅ Compatible - String foreign key reference
- **Session ID**: ✅ Compatible - UUID string fits VARCHAR(255)

---

## Table 3: `palette_analyse` (Emotion Analysis Results)

### Database Expected Format

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| `session_id` | `VARCHAR(255)` | `PRIMARY KEY` | Foreign key to user_session (one analysis per session) |
| `gifname` | `VARCHAR(255)` | `NULL` | Name of the GIF file analyzed |
| `anger` | `DECIMAL(5,4)` | `NULL` | Emotion probability (0.0000-1.0000) |
| `anticipation` | `DECIMAL(5,4)` | `NULL` | Emotion probability (0.0000-1.0000) |
| `arrogance` | `DECIMAL(5,4)` | `NULL` | Emotion probability (0.0000-1.0000) |
| `disagreeableness` | `DECIMAL(5,4)` | `NULL` | Emotion probability (0.0000-1.0000) |
| `disgust` | `DECIMAL(5,4)` | `NULL` | Emotion probability (0.0000-1.0000) |
| `fear` | `DECIMAL(5,4)` | `NULL` | Emotion probability (0.0000-1.0000) |
| `gratitude` | `DECIMAL(5,4)` | `NULL` | Emotion probability (0.0000-1.0000) |
| `happiness` | `DECIMAL(5,4)` | `NULL` | Emotion probability (0.0000-1.0000) |
| `humility` | `DECIMAL(5,4)` | `NULL` | Emotion probability (0.0000-1.0000) |
| `love` | `DECIMAL(5,4)` | `NULL` | Emotion probability (0.0000-1.0000) |
| `optimism` | `DECIMAL(5,4)` | `NULL` | Emotion probability (0.0000-1.0000) |
| `pessimism` | `DECIMAL(5,4)` | `NULL` | Emotion probability (0.0000-1.0000) |
| `sadness` | `DECIMAL(5,4)` | `NULL` | Emotion probability (0.0000-1.0000) |
| `surprise` | `DECIMAL(5,4)` | `NULL` | Emotion probability (0.0000-1.0000) |
| `trust` | `DECIMAL(5,4)` | `NULL` | Emotion probability (0.0000-1.0000) |
| `created_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP` | Auto-generated |
| `updated_at` | `TIMESTAMP` | `ON UPDATE CURRENT_TIMESTAMP` | Auto-managed |

### Server Data Being Sent

**From `/capture-palette` endpoint:**
```python
emotion_data = result.get('emotionPrediction', {})
all_probabilities = emotion_data.get('all_probabilities', {})

db.save_palette_analyse(
    session_id=session_id,              # String (UUID)
    gifname=gif_name,                   # String (e.g., "5.gif")
    emotion_scores=all_probabilities    # Dict[str, float] - emotion names to probabilities
)
```

### ✅ Compatibility Analysis
- **Session ID**: ✅ Compatible - UUID string fits VARCHAR(255)
- **GIF Name**: ✅ Compatible - Filename string fits VARCHAR(255)
- **Emotion Scores**: ✅ Compatible - Float values (0.0-1.0) fit DECIMAL(5,4)
- **Named Emotions**: ✅ Compatible - All 15 emotions have dedicated columns

---

## Table 4: `painting_recommendations` (Recommended Painting URLs)

### Database Expected Format

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| `session_id` | `VARCHAR(255)` | `PRIMARY KEY` | Foreign key to user_session (one set per session) |
| `url_0` to `url_9` | `TEXT` | `NULL` | Painting URLs (10 total) |
| `created_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP` | Auto-generated |
| `updated_at` | `TIMESTAMP` | `ON UPDATE CURRENT_TIMESTAMP` | Auto-managed |

### Server Data Being Sent

**From `/capture-palette` endpoint:**
```python
painting_urls = result.get('urls', [])[:10]

db.save_painting_recommendations(
    session_id=session_id,      # String (UUID)  
    urls=painting_urls          # List[String] - up to 10 URLs
)
```

### ✅ Compatibility Analysis
- **Session ID**: ✅ Compatible - UUID string fits VARCHAR(255)
- **Painting URLs**: ✅ Compatible - URLs fit TEXT type, list padded/truncated to 10

---

## Table 5: `emotion_selection` (User's Selected Emotion)

### Database Expected Format

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| `session_id` | `VARCHAR(255)` | `PRIMARY KEY` | Foreign key to user_session (one selection per session) |
| `selected_emotion` | `VARCHAR(100)` | `NULL` | User's chosen emotion |
| `created_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP` | Auto-generated |
| `updated_at` | `TIMESTAMP` | `ON UPDATE CURRENT_TIMESTAMP` | Auto-managed |

### Server Data Being Sent

**From `/save-emotion` endpoint:**
```python
db.save_emotion_selection(
    session_id=session_id,      # String (UUID)
    selected_emotion=emotion    # String (emotion name)
)
```

### ✅ Compatibility Analysis
- **Session ID**: ✅ Compatible - UUID string fits VARCHAR(255)
- **Selected Emotion**: ✅ Compatible - Emotion name fits VARCHAR(100)

---

## Table 6: `paintings_style` (User's Selected Paintings and Character)

### Database Expected Format

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| `session_id` | `VARCHAR(255)` | `PRIMARY KEY` | Foreign key to user_session (one selection per session) |
| `url_0` to `url_2` | `TEXT` | `NULL` | Selected painting URLs (3 total) |
| `story_character` | `VARCHAR(100)` | `NULL` | Chosen story character type |
| `nickname` | `VARCHAR(255)` | `NULL` | User's story nickname |
| `created_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP` | Auto-generated |
| `updated_at` | `TIMESTAMP` | `ON UPDATE CURRENT_TIMESTAMP` | Auto-managed |

### Server Data Being Sent

**From `/save-selection` endpoint:**
```python
painting_urls = [p.get('url', '') for p in selected_paintings]

db.save_paintings_style(
    session_id=session_id,          # String (UUID)
    painting_urls=painting_urls,    # List[String] - 3 URLs
    story_character=character,      # String (e.g., "poet", "historian")
    nickname=nickname               # String
)
```

### ✅ Compatibility Analysis
- **Session ID**: ✅ Compatible - UUID string fits VARCHAR(255)
- **Painting URLs**: ✅ Compatible - URLs fit TEXT type, list padded/truncated to 3
- **Story Character**: ✅ Compatible - Character name fits VARCHAR(100)
- **Nickname**: ✅ Compatible - String fits VARCHAR(255)

---

## Table 7: `feedback_form` (User Feedback)

### Database Expected Format

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| `session_id` | `VARCHAR(255)` | `PRIMARY KEY` | Foreign key to user_session (one feedback per session) |
| `q1` to `q13` | `INT` | `NULL` | Survey question responses (integers) |
| `q14`, `q15` | `TEXT` | `NULL` | Long text responses |
| `created_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP` | Auto-generated |
| `updated_at` | `TIMESTAMP` | `ON UPDATE CURRENT_TIMESTAMP` | Auto-managed |

### Server Data Being Sent

**From `/submit-feedback` endpoint:**
```python
# Extract answers data (q1-q13 as integers 1-5, q14-q15 as text)
answers = data.get('answers', {})

feedback_form_data = {
    'q1': answers.get('q1'),        # Integer (1-5) - Website ease of use
    'q2': answers.get('q2'),        # Integer (1-5) - Navigation smoothness  
    'q3': answers.get('q3'),        # Integer (1-5) - Visual design
    'q4': answers.get('q4'),        # Integer (1-5) - Perfect palette resonance
    'q5': answers.get('q5'),        # Integer (1-5) - Color/emotion insights
    'q6': answers.get('q6'),        # Integer (1-5) - Painting recommendations
    'q7': answers.get('q7'),        # Integer (1-5) - Story consistency
    'q8': answers.get('q8'),        # Integer (1-5) - Emotional responses
    'q9': answers.get('q9'),        # Integer (1-5) - Engaging experience
    'q10': answers.get('q10'),      # Integer (1-5) - Immersion in journey
    'q11': answers.get('q11'),      # Integer (1-5) - Meaningful art discovery
    'q12': answers.get('q12'),      # Integer (1-5) - Future use interest
    'q13': answers.get('q13'),      # Integer (1-5) - Recommendation to friends
    'q14': answers.get('q14'),      # String (TEXT) - What they liked most
    'q15': answers.get('q15')       # String (TEXT) - Improvement suggestions
}

db.save_feedback_form(
    session_id=session_id,
    feedback_data=feedback_form_data
)
```

### ✅ Compatibility Analysis
- **Session ID**: ✅ Compatible - UUID string fits VARCHAR(255)
- **Survey Questions (q1-q13)**: ✅ Compatible - Integers fit INT type
- **Text Responses (q14-q15)**: ✅ Compatible - Strings fit TEXT type

---

## Data Flow Summary

### **No-ID Schema Benefits** ✅

1. **Simplified Structure**: No redundant ID columns, natural keys as primary keys
2. **Reduced Storage**: Smaller table footprint without extra integer columns
3. **Foreign Key Integrity**: Cascading deletes ensure data consistency
4. **Flexible Age Handling**: VARCHAR allows age ranges like "25-34"
5. **Dedicated Emotion Storage**: Named columns for all 15 emotions
6. **Clean Session Management**: Direct session_id relationships
7. **One-to-One Guarantees**: Each session can only have one record per table (enforced by PRIMARY KEY)

### **All Data Flows Working** ✅

1. **User Registration**: `/store-username` → `user_info` table ✅
2. **Session Creation**: `/create-session` → `user_session` table ✅
3. **Palette Analysis**: `/capture-palette` → `palette_analyse` + `painting_recommendations` ✅
4. **Emotion Selection**: `/save-emotion` → `emotion_selection` table ✅
5. **Painting Selection**: `/save-selection` → `paintings_style` table ✅
6. **Feedback Submission**: `/submit-feedback` → `feedback_form` table ✅

### **Database Connection Status**

- **Connection Method**: `mysql.connector` with connection pooling
- **Character Set**: `utf8mb4` (supports emojis and international characters)
- **Transaction Support**: Auto-commit enabled
- **Error Handling**: Proper exception handling with logging
- **SQL Mode**: `STRICT_TRANS_TABLES` (prevents invalid data)
- **Foreign Key Constraints**: Enabled with CASCADE deletes

---

## Endpoint to Table Mapping

| Endpoint | HTTP Method | Target Table(s) | Purpose |
|----------|-------------|-----------------|---------|
| `/store-username` | POST | `user_info` | Store user demographics |
| `/create-session` | POST | `user_session` | Link user to new session |
| `/capture-palette` | POST | `palette_analyse`, `painting_recommendations` | Save emotion analysis and recommendations |
| `/save-emotion` | POST | `emotion_selection` | Save user's emotion choice |
| `/save-selection` | POST | `paintings_style` | Save painting selections and character |
| `/submit-feedback` | POST | `feedback_form` | Save user feedback and survey |

---

## Recommendations

### **Current Status**
- **Overall**: 🟢 **Fully Functional** - All endpoints properly integrated
- **Data Integrity**: 🟢 **Strong** - Foreign key constraints enforce relationships
- **Schema Design**: 🟢 **Simplified** - Natural keys eliminate redundancy
- **Performance**: 🟡 **Good** - String primary keys slightly slower than integers but acceptable
- **Storage**: 🟢 **Optimized** - Reduced storage without ID columns

### **Maintenance Benefits**
1. **Simplified Data Structure**: No redundant ID columns to track
2. **Easy Analytics**: Data can be easily joined using natural keys
3. **One-to-One Enforcement**: Primary key constraints ensure data uniqueness
4. **Data Export**: Clean CSV export functionality for research purposes
5. **Backup/Recovery**: Individual table backup and restoration possible
6. **Business Logic Alignment**: Primary keys match natural business identifiers 