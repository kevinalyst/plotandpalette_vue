import os
import json
import sys
import base64
from typing import List, Dict
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ImageStoryGenerator:
    def __init__(self):
        # Read OpenAI API key from environment (do not hardcode secrets)
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.client = None
        self._api_call_count = 0
        self._api_call_log = []
        
        # Define the core framework template
        self.core_framework = """# PROMPT FOR NARRATIVE GENERATION

## 1. CORE OBJECTIVE
Write a cohesive and compelling micro-story of approximately 300 words. The story must connect the three paintings provided below into a single, continuous narrative, presented in a specific narrative style.

{nickname_instruction}

IMPORTANT: Structure your response in exactly three distinct sections, each tied to one painting. Use the following format:

**PAINTING_1_SECTION**
[Write approximately 100 words for this section]

**PAINTING_2_SECTION**
[Write approximately 100 words for this section]

**PAINTING_3_SECTION**
[Write approximately 100 words for this section]

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

Structure: Beginning (Painting 1) → Development (Painting 2) → Conclusion (Painting 3)
Length: Exactly 300 words total (approximately 100 words per section)

CRITICAL: You must use the exact section markers **PAINTING_1_SECTION**, **PAINTING_2_SECTION**, and **PAINTING_3_SECTION** to clearly divide your story into three parts."""
        
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
        """Initialize the OpenAI client only when needed for API calls"""
        if self.client is None:
            # OpenAI client reads key from env or explicit param
            self.client = OpenAI(api_key=self.api_key)
            print(f"[API] OpenAI client initialized for image story generation", file=sys.stderr)
    
    def _encode_image(self, image_path: str) -> tuple:
        """Encode image to base64 for OpenAI API and determine media type"""
        try:
            # Determine media type based on file extension
            file_ext = os.path.splitext(image_path)[1].lower()
            if file_ext in ['.jpg', '.jpeg']:
                media_type = 'image/jpeg'
            elif file_ext == '.png':
                media_type = 'image/png'
            elif file_ext == '.gif':
                media_type = 'image/gif'
            elif file_ext == '.webp':
                media_type = 'image/webp'
            else:
                # Default to JPEG for unknown formats
                media_type = 'image/jpeg'
            
            with open(image_path, 'rb') as image_file:
                encoded_data = base64.b64encode(image_file.read()).decode('utf-8')
                return encoded_data, media_type
        except Exception as e:
            print(f"[ERROR] Failed to encode image {image_path}: {e}", file=sys.stderr)
            raise
    
    def _parse_structured_story(self, story_text: str) -> Dict:
        """Parse the structured story response into three distinct parts"""
        try:
            # Split the story by section markers
            sections = {}
            
            # Define section markers
            markers = ['**PAINTING_1_SECTION**', '**PAINTING_2_SECTION**', '**PAINTING_3_SECTION**']
            
            # Split text by markers
            parts = story_text.split('**PAINTING_1_SECTION**')
            if len(parts) > 1:
                remaining_text = parts[1]
                
                # Extract section 1
                section_2_split = remaining_text.split('**PAINTING_2_SECTION**')
                if len(section_2_split) > 1:
                    sections['story_part_1'] = section_2_split[0].strip()
                    remaining_text = section_2_split[1]
                    
                    # Extract section 2 and 3
                    section_3_split = remaining_text.split('**PAINTING_3_SECTION**')
                    if len(section_3_split) > 1:
                        sections['story_part_2'] = section_3_split[0].strip()
                        sections['story_part_3'] = section_3_split[1].strip()
                    else:
                        # If section 3 marker not found, put remaining text in section 2
                        sections['story_part_2'] = remaining_text.strip()
                        sections['story_part_3'] = ""
                else:
                    # If section 2 marker not found, put all text in section 1
                    sections['story_part_1'] = remaining_text.strip()
                    sections['story_part_2'] = ""
                    sections['story_part_3'] = ""
            else:
                # If no markers found, split the story into three equal parts
                words = story_text.split()
                words_per_section = len(words) // 3
                
                sections['story_part_1'] = ' '.join(words[:words_per_section])
                sections['story_part_2'] = ' '.join(words[words_per_section:words_per_section*2])
                sections['story_part_3'] = ' '.join(words[words_per_section*2:])
                
                print(f"[WARNING] No section markers found, split story into equal parts", file=sys.stderr)
            
            # Ensure all sections exist
            for key in ['story_part_1', 'story_part_2', 'story_part_3']:
                if key not in sections:
                    sections[key] = ""
            
            return sections
            
        except Exception as e:
            print(f"[ERROR] Failed to parse structured story: {e}", file=sys.stderr)
            # Fallback: split into three equal parts
            words = story_text.split()
            words_per_section = len(words) // 3
            
            return {
                'story_part_1': ' '.join(words[:words_per_section]),
                'story_part_2': ' '.join(words[words_per_section:words_per_section*2]),
                'story_part_3': ' '.join(words[words_per_section*2:])
            }
    
    def _classify_intensity(self, probability: float) -> str:
        """Classify emotional intensity based on probability percentage"""
        if probability <= 0.3:
            return "Low"
        elif probability <= 0.5:
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
    
    def generate_story(self, paintings: List[Dict], narrative_style: str, nickname: str = None, emotion: str = None, emotion_probability: float = None) -> Dict:
        """Generate story based on painting images, narrative style, and user emotion"""
        
        # Validate inputs
        if len(paintings) != 3:
            raise ValueError("Exactly 3 paintings must be provided")
        
        if narrative_style not in self.narrative_style_blocks:
            raise ValueError(f"Invalid narrative style. Must be one of: {list(self.narrative_style_blocks.keys())}")
        
        # Verify image paths exist - REQUIRED for image-based story generation
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
            
            # Prepare nickname instruction
            nickname_instruction = ""
            if nickname and nickname.strip():
                nickname_instruction = f"\n\nCRITICAL NARRATIVE REQUIREMENT: This story MUST be written in first person from the perspective of '{nickname.strip()}'. \n\n**MANDATORY FOR PAINTING_1_SECTION**: Begin the first section with a clear self-introduction using EXACTLY this format: 'I am {nickname.strip()}, and...' or 'My name is {nickname.strip()}, and I...' \n\nThroughout ALL sections, use first-person pronouns (I, me, my, myself) and maintain the narrator's identity as {nickname.strip()}. The story should feel like {nickname.strip()} is personally experiencing and observing these artworks."
            
            # Build the complete prompt using the modular structure
            complete_prompt = self.core_framework.format(
                narrative_style_name=style_block["name"],
                primary_emotion=emotion,
                emotional_intensity=intensity,
                narrative_style_definition=style_block["definition"],
                dynamic_guidance=dynamic_guidance,
                painting1_title=paintings[0]['title'],
                painting1_artist=paintings[0]['artist'],
                painting1_year=paintings[0].get('year', ''),
                painting2_title=paintings[1]['title'],
                painting2_artist=paintings[1]['artist'],
                painting2_year=paintings[1].get('year', ''),
                painting3_title=paintings[2]['title'],
                painting3_artist=paintings[2]['artist'],
                painting3_year=paintings[2].get('year', ''),
                nickname_instruction=nickname_instruction
            )
            
            # Prepare the chat message with text and images (Chat Completions multimodal)
            # Use data URLs to embed base64 images
            user_content = [
                {"type": "text", "text": complete_prompt}
            ]

            for i, painting in enumerate(paintings):
                try:
                    image_data, media_type = self._encode_image(painting['imagePath'])
                    data_url = f"data:{media_type};base64,{image_data}"
                    user_content.append({
                        "type": "image_url",
                        "image_url": {"url": data_url}
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
            
            # Call OpenAI Chat Completions with images (GPT-5)
            completion = self.client.chat.completions.create(
                model="gpt-5",
                temperature=0.8,
                max_tokens=1000,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a creative writer specializing in art narratives. Use both the provided artwork information and your visual analysis of the images to create rich, detailed stories. Follow the modular prompt structure exactly and always write exactly 300 words."
                    },
                    {
                        "role": "user",
                        "content": user_content
                    }
                ]
            )

            story_text = completion.choices[0].message.content
            
            # Parse the structured story into three parts
            story_parts = self._parse_structured_story(story_text)
            
            # Generate a compelling story title based on the actual story content
            title_prompt = f"""Based on the following story, create a compelling and evocative title (maximum 8 words) that captures the essence and main theme of the narrative. The title should be poetic, memorable, and reflective of the story's central message or imagery.

Story:
{story_text}

Generate only the title, nothing else."""

            # Generate the story title using a separate OpenAI call
            title_completion = self.client.chat.completions.create(
                model="gpt-5",
                temperature=0.7,
                max_tokens=50,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a skilled title writer. Create evocative, poetic titles that capture the essence of stories. Keep titles under 8 words."
                    },
                    {
                        "role": "user",
                        "content": title_prompt
                    }
                ]
            )

            generated_title = title_completion.choices[0].message.content.strip()
            # Remove quotes if the AI added them
            if generated_title.startswith('"') and generated_title.endswith('"'):
                generated_title = generated_title[1:-1]
            if generated_title.startswith("'") and generated_title.endswith("'"):
                generated_title = generated_title[1:-1]
            
            # Update API call tracking (now 2 calls made)
            self._api_call_count += 2  # Story + title generation
            api_call_info['success'] = True
            api_call_info['word_count'] = len(story_text.split())
            api_call_info['generated_title'] = generated_title
            self._api_call_log.append(api_call_info)
            
            print(f"[API] Story and title generated successfully ({len(story_text.split())} words)", file=sys.stderr)
            print(f"[API] Generated title: {generated_title}", file=sys.stderr)
            print(f"[API] Story parts parsed: {len(story_parts['story_part_1'].split())} + {len(story_parts['story_part_2'].split())} + {len(story_parts['story_part_3'].split())} words", file=sys.stderr)
            
            return {
                'success': True,
                'story': story_text,
                'story_title': generated_title,  # The AI-generated title based on story content
                'story_part_1': story_parts['story_part_1'],
                'story_part_2': story_parts['story_part_2'],
                'story_part_3': story_parts['story_part_3'],
                'narrative_style': style_block['name'],  # Keep the narrative style separate
                'paintings': paintings,
                'word_count': len(story_text.split()),
                'nickname': nickname,
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
        nickname = input_data.get('nickname', '')
        emotion = input_data.get('emotion', None)
        emotion_probability = input_data.get('emotion_probability', None)
        
        # Create generator and generate story
        generator = ImageStoryGenerator()
        result = generator.generate_story(
            paintings=paintings, 
            narrative_style=narrative_style, 
            nickname=nickname,
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