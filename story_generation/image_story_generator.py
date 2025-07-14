import os
import json
import sys
import base64
from typing import List, Dict
import anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ImageStoryGenerator:
    def __init__(self):
        self.api_key = os.getenv('CLAUDE_API_KEY')
        if not self.api_key:
            raise ValueError("CLAUDE_API_KEY not found in environment variables")
        
        self.client = None
        self._api_call_count = 0
        self._api_call_log = []
        
        # Define the core framework template
        self.core_framework = """# PROMPT FOR NARRATIVE GENERATION

## 1. CORE OBJECTIVE
Write a cohesive and compelling micro-story of approximately 300 words. The story must connect the three paintings provided below into a single, continuous narrative, presented in a specific narrative style.

## 2. KEY INPUTS
* **Narrative Style:** {narrative_style_name}
* **Primary Emotion:** {primary_emotion}
* **Emotional Intensity:** {emotional_intensity}

---

## 3. NARRATIVE STYLE DEFINITION
{narrative_style_definition}

---

## 4. DYNAMIC GUIDANCE (EMOTION & INTENSITY)
{dynamic_guidance}

---

## 5. CONTEXT: THE PAINTINGS
Your narrative must be anchored to the following three artworks in the specified sequence.

* **Painting 1 (The Beginning):**
   * **Title:** `{painting1_title}`
   * **Artist:** `{painting1_artist}`
   * **Year:** `{painting1_year}`

* **Painting 2 (The Middle):**
   * **Title:** `{painting2_title}`
   * **Artist:** `{painting2_artist}`
   * **Year:** `{painting2_year}`

* **Painting 3 (The End):**
   * **Title:** `{painting3_title}`
   * **Artist:** `{painting3_artist}`
   * **Year:** `{painting3_year}`

IMPORTANT: I am also providing you with images of these three paintings. Use both the artwork information above AND your visual analysis of the actual images to create a richer, more detailed story. Incorporate what you can observe in the paintings: colors, composition, brushwork, style, mood, and visual elements to enhance your narrative.

{user_name_instruction}

Structure: Beginning (Painting 1) → Development (Painting 2) → Conclusion (Painting 3)
Length: Exactly 300 words"""
        
        # Define the narrative style blocks
        self.narrative_style_blocks = {
            "historian": {
                "name": "The Historian's Chronicle",
                "definition": """**Role Assignment:** You are an engaging art historian and a master storyteller. Your voice is knowledgeable, clear, and authoritative, excelling at connecting individual artworks to the grand sweep of history.

**Stylistic Instructions:**
* DO: Weave a chronological or thematic thread that logically connects the three paintings. Focus on factual elements: the artist's biography, the social and political context of the era, or the artwork's provenance.
* DO NOT: Invent fictional events or characters. Your tone is that of an expert guide, not abstract poetry."""
            },
            
            "poet": {
                "name": "The Poet's Dream",
                "definition": """**Role Assignment:** You are a lyrical poet, a master of evocative and metaphorical language. Your voice is expressive and imaginative, attuned to mood and feeling.

**Stylistic Instructions:**
* DO: Use rich, metaphorical language and vivid sensory details to focus on the mood and atmosphere of the art. The story should be an emotional journey.
* DO NOT: Provide dry, academic analysis. Instead of describing the paintings, interpret their essence through poetic language."""
            },
            
            "detective": {
                "name": "The Detective's Case",
                "definition": """**Role Assignment:** You are a brilliant detective with a keen eye for symbolism and a flair for the dramatic. Your voice is sharp, inquisitive, and suspenseful.

**Stylistic Instructions:**
* DO: Build suspense using foreshadowing, rhetorical questions, and the gradual reveal of clues. Treat the paintings as crime scenes or pieces of evidence, focusing on symbols and hidden details.
* DO NOT: Reveal the entire mystery until the final sentences. Maintain intrigue throughout."""
            },
            
            "critic": {
                "name": "The Critic's Analysis",
                "definition": """**Role Assignment:** You are an eloquent and highly perceptive art critic with a gift for explaining complex ideas in an accessible way. Your voice is intelligent, insightful, and analytical.

**Stylistic Instructions:**
* DO: Focus on formal elements like composition, color theory, light, and brushwork. Explain how these technical choices create a narrative and evoke the primary emotion.
* DO NOT: Invent a fictional story. The narrative you describe is the one created by the artists' techniques. Avoid overly academic jargon."""
            },
            
            "time_traveller": {
                "name": "The Time Traveller's Report",
                "definition": """**Role Assignment:** You are a witty, observant, and slightly irreverent time traveler, reporting on the past with a modern sensibility and a sharp sense of humor.

**Stylistic Instructions:**
* DO: Adopt a humorous, conversational tone. Create anachronistic connections and find modern parallels in the scenes.
* DO NOT: Be overly reverent or historical. The goal is entertainment and clever observation. Use the paintings as settings for your imaginative tale."""
            }
        }
    
    def _initialize_client_if_needed(self):
        """Initialize the Claude client only when needed for API calls"""
        if self.client is None:
            self.client = anthropic.Anthropic(api_key=self.api_key)
            print(f"[API] Claude client initialized for image story generation", file=sys.stderr)
    
    def _encode_image(self, image_path: str) -> str:
        """Encode image to base64 for Claude API"""
        try:
            with open(image_path, 'rb') as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            print(f"[ERROR] Failed to encode image {image_path}: {e}", file=sys.stderr)
            raise
    
    def _classify_intensity(self, probability: float) -> str:
        """Classify emotional intensity based on probability percentage"""
        if probability <= 30:
            return "Low"
        elif probability <= 50:
            return "Medium"
        else:
            return "High"
    
    def _generate_dynamic_guidance(self, emotion: str, intensity: str) -> str:
        """Generate dynamic guidance based on emotion and intensity"""
        
        base_guidance = f"The central emotional theme of the narrative is **{emotion}**."
        
        if intensity == "Low":
            return f"""{base_guidance}

**Intensity Level: Low**
The emotional tone should be subtle and understated. Weave a gentle undercurrent of {emotion} through the narrative, focusing on quiet details and suggestive atmosphere.

* **Beginning (Painting 1):** Introduce a hint of {emotion}.
* **Middle (Painting 2):** Allow the feeling to linger or shift subtly.
* **End (Painting 3):** Conclude with a sense of quiet resignation or gentle resolution related to {emotion}."""
        
        elif intensity == "Medium":
            return f"""{base_guidance}

**Intensity Level: Medium**
The emotional tone should be clear and central to the plot. The story must directly reflect a journey of {emotion}.

* **Beginning (Painting 1):** Clearly establish the theme of {emotion}.
* **Middle (Painting 2):** Develop or complicate this emotion, showing a direct consequence or progression.
* **End (Painting 3):** Provide a distinct resolution to the emotional arc of {emotion}."""
        
        else:  # High intensity
            return f"""{base_guidance}

**Intensity Level: High**
The emotional tone must be powerful and dramatic. The narrative should be driven by an intense and escalating feeling of {emotion}.

* **Beginning (Painting 1):** Open with a strong, immersive sense of {emotion}.
* **Middle (Painting 2):** Escalate the emotion to a dramatic peak, raising the stakes significantly.
* **End (Painting 3):** Conclude with a powerful, cathartic, or overwhelming culmination of the {emotion} journey."""
    
    def generate_story(self, paintings: List[Dict], narrative_style: str, user_name: str = None, emotion: str = None, emotion_probability: float = None) -> Dict:
        """Generate story based on painting images, narrative style, and user emotion"""
        
        # Validate inputs
        if len(paintings) != 3:
            raise ValueError("Exactly 3 paintings must be provided")
        
        if narrative_style not in self.narrative_style_blocks:
            raise ValueError(f"Invalid narrative style. Must be one of: {list(self.narrative_style_blocks.keys())}")
        
        # Verify image paths exist
        for i, painting in enumerate(paintings):
            if 'imagePath' not in painting:
                raise ValueError(f"Image path missing for painting {i+1}")
            if not os.path.exists(painting['imagePath']):
                raise ValueError(f"Image file not found: {painting['imagePath']}")
        
        # Handle emotion and intensity (use defaults if not provided)
        if emotion is None:
            emotion = "wonder"
            emotion_probability = 50.0
            print(f"[INFO] No emotion provided, using default: {emotion} ({emotion_probability}%)", file=sys.stderr)
        
        if emotion_probability is None:
            emotion_probability = 50.0
            print(f"[INFO] No emotion probability provided, using default: {emotion_probability}%", file=sys.stderr)
        
        intensity = self._classify_intensity(emotion_probability)
        
        print(f"[INFO] Emotion: {emotion}, Probability: {emotion_probability}%, Intensity: {intensity}", file=sys.stderr)
        
        try:
            # Initialize client
            self._initialize_client_if_needed()
            
            # Get narrative style block
            style_block = self.narrative_style_blocks[narrative_style]
            
            # Generate dynamic guidance
            dynamic_guidance = self._generate_dynamic_guidance(emotion, intensity)
            
            # Prepare user name instruction
            user_name_instruction = ""
            if user_name and user_name.strip():
                user_name_instruction = f"\n\nIMPORTANT: The story should be written in first person from the perspective of '{user_name.strip()}'. Begin the story with a brief self-introduction such as 'I am {user_name.strip()}, and...' or 'My name is {user_name.strip()}, and I...' The narrator should use first-person pronouns (I, me, my) throughout the story while clearly establishing their identity as {user_name.strip()} at the beginning."
            
            # Build the complete prompt using the modular structure
            complete_prompt = self.core_framework.format(
                narrative_style_name=style_block["name"],
                primary_emotion=emotion,
                emotional_intensity=intensity,
                narrative_style_definition=style_block["definition"],
                dynamic_guidance=dynamic_guidance,
                painting1_title=paintings[0]['title'],
                painting1_artist=paintings[0]['artist'],
                painting1_year=paintings[0]['year'],
                painting2_title=paintings[1]['title'],
                painting2_artist=paintings[1]['artist'],
                painting2_year=paintings[1]['year'],
                painting3_title=paintings[2]['title'],
                painting3_artist=paintings[2]['artist'],
                painting3_year=paintings[2]['year'],
                user_name_instruction=user_name_instruction
            )
            
            # Prepare the message with formatted text prompt and images
            message_content = [
                {
                    "type": "text",
                    "text": complete_prompt
                }
            ]
            
            # Add images to the message
            for i, painting in enumerate(paintings):
                try:
                    image_data = self._encode_image(painting['imagePath'])
                    message_content.append({
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": image_data
                        }
                    })
                except Exception as e:
                    print(f"[ERROR] Failed to process image {i+1}: {e}", file=sys.stderr)
                    raise
            
            # Log API call
            api_call_info = {
                'timestamp': os.popen('date').read().strip(),
                'narrative_style': narrative_style,
                'emotion': emotion,
                'emotion_probability': emotion_probability,
                'intensity': intensity,
                'paintings': [f"{p.get('title', 'Unknown')} by {p.get('artist', 'Unknown')}" for p in paintings],
                'call_number': self._api_call_count + 1,
                'with_images': True
            }
            
            print(f"[API] Making emotion-driven story generation call #{self._api_call_count + 1}", file=sys.stderr)
            print(f"[API] Style: {narrative_style}", file=sys.stderr)
            print(f"[API] Emotion: {emotion} ({emotion_probability}% -> {intensity} intensity)", file=sys.stderr)
            print(f"[API] Images: {[p.get('title', 'Unknown') for p in paintings]}", file=sys.stderr)
            
            # Call Claude API with images
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",  # Using Claude 3.5 for better vision capabilities
                max_tokens=600,
                temperature=0.8,
                system="You are a creative writer specializing in art narratives. Use both the provided artwork information and your visual analysis of the images to create rich, detailed stories. Follow the modular prompt structure exactly and always write exactly 300 words.",
                messages=[
                    {
                        "role": "user",
                        "content": message_content
                    }
                ]
            )
            
            story_text = message.content[0].text
            
            # Update API call tracking
            self._api_call_count += 1
            api_call_info['success'] = True
            api_call_info['word_count'] = len(story_text.split())
            self._api_call_log.append(api_call_info)
            
            print(f"[API] Emotion-driven story generated successfully ({len(story_text.split())} words)", file=sys.stderr)
            
            # Format title using proper narrative style names and user's name
            if user_name and user_name.strip():
                story_title = f"{style_block['name']} - {user_name.strip()}"
            else:
                story_title = style_block['name']
            
            return {
                'success': True,
                'story': story_text,
                'narrative_style': story_title,
                'paintings': paintings,
                'word_count': len(story_text.split()),
                'user_name': user_name,
                'emotion': emotion,
                'emotion_probability': emotion_probability,
                'intensity': intensity
            }
            
        except Exception as e:
            # Log failed API call
            self._api_call_log.append({
                'timestamp': os.popen('date').read().strip(),
                'narrative_style': narrative_style,
                'emotion': emotion,
                'emotion_probability': emotion_probability,
                'intensity': intensity if 'intensity' in locals() else None,
                'paintings': [f"{p.get('title', 'Unknown')} by {p.get('artist', 'Unknown')}" for p in paintings],
                'call_number': self._api_call_count + 1,
                'success': False,
                'error': str(e),
                'with_images': True
            })
            
            return {
                'success': False,
                'error': str(e),
                'narrative_style': narrative_style,
                'paintings': paintings,
                'emotion': emotion,
                'emotion_probability': emotion_probability
            }
    
    def get_api_usage_stats(self) -> Dict:
        """Get statistics about API usage"""
        return {
            'total_api_calls': self._api_call_count,
            'api_call_log': self._api_call_log,
            'client_initialized': self.client is not None
        }

def main():
    """Main function for command-line usage"""
    if len(sys.argv) < 2:
        print("Usage: python image_story_generator.py '<json_input>'")
        sys.exit(1)
    
    try:
        # Parse input JSON
        input_data = json.loads(sys.argv[1])
        
        # Extract data
        paintings = input_data.get('paintings', [])
        narrative_style = input_data.get('narrative_style', '')
        user_name = input_data.get('user_name', '')
        emotion = input_data.get('emotion', None)
        emotion_probability = input_data.get('emotion_probability', None)
        
        # Create generator and generate story
        generator = ImageStoryGenerator()
        result = generator.generate_story(
            paintings=paintings, 
            narrative_style=narrative_style, 
            user_name=user_name,
            emotion=emotion,
            emotion_probability=emotion_probability
        )
        
        # Output result as JSON
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        error_result = {
            'success': False,
            'error': str(e)
        }
        print(json.dumps(error_result, indent=2))
        sys.exit(1)

if __name__ == "__main__":
    main() 