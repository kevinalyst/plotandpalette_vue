# Story Generation Module

This module integrates Claude AI to generate creative narratives based on user-selected paintings and narrative styles.

## Setup

1. **Install Dependencies**
   ```bash
   cd story_generation
   pip install -r requirements.txt
   ```

2. **Configure API Key**
   ```bash
   python3 setup_env.py
   ```
   This will create a `.env` file with your Claude API key.

3. **Test the Module**
   ```bash
   python3 test_story.py
   ```

## Narrative Styles

The module supports 5 distinct narrative styles:

1. **The Historian's Chronicle** - Academic, historical analysis
2. **The Poet's Dream** - Lyrical, emotional interpretation
3. **The Detective's Case** - Mystery-focused investigation
4. **The Critic's Analysis** - Sophisticated art criticism
5. **The Time Traveller's Report** - Immersive historical journey

## API Usage

### From Python:
```python
from story_generator import StoryGenerator

generator = StoryGenerator()
result = generator.generate_story(
    paintings=[
        {"title": "...", "artist": "...", "year": "..."},
        # ... 3 paintings total
    ],
    narrative_style="historian"  # or poet, detective, critic, time_traveller
)
```

### From Server (via endpoint):
```javascript
fetch('/api/generate-story', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        paintings: [...],  // Array of 3 painting objects
        narrativeStyle: 'historian'
    })
})
```

## Response Format

```json
{
    "success": true,
    "story": "The generated 300-word narrative...",
    "narrative_style": "The Historian's Chronicle",
    "paintings": [...],
    "word_count": 300
}
```

## Error Handling

The module handles various error cases:
- Missing API key
- Invalid narrative style
- Incorrect number of paintings
- API request failures

All errors return a standardized error response with `success: false` and an error message. 