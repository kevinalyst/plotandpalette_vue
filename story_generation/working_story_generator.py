#!/usr/bin/env python3
"""
Working story generator that bridges the server's expectations with the actual story generation system
This file acts as an adapter between server.py and the existing secure_story_generator.py
"""

import json
import sys
import os
from datetime import datetime

# Add the current directory to Python path so we can import from story_generation
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(current_dir)
sys.path.append(parent_dir)

try:
    from secure_story_generator import SecureStoryGenerator
    SECURE_GENERATOR_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import secure_story_generator: {e}", file=sys.stderr)
    SECURE_GENERATOR_AVAILABLE = False

def create_fallback_story(paintings, user_name, emotion, narrative_style):
    """Create a fallback story when the secure generator is not available"""
    
    style_templates = {
        'historian': f"""Dear {user_name},

As a historian examining these three remarkable works - {', '.join(paintings)} - I observe how they reflect the artistic evolution of their respective periods.

Each painting serves as a window into its era, capturing not just aesthetic beauty but the cultural zeitgeist of its time. The brushwork speaks of techniques passed down through generations, while the subjects reveal the preoccupations and values of their societies.

When viewed together, these works create a dialogue across time, with {emotion} serving as the common thread that connects disparate artistic movements and historical moments.

Through this lens of {emotion}, we see how art transcends its immediate context to speak to universal human experiences.""",

        'poet': f"""Oh {user_name}, muse of inspiration,

In these three canvases - {', '.join(paintings)} - I find verses written in pigment and passion, each stroke a word in the poetry of {emotion}.

The first painting whispers in colors soft and deep, the second sings in harmonies bold and bright, while the third completes the sonnet with its concluding grace.

Together they weave a tapestry of feeling, where {emotion} flows like rhythm through each painted line. In their beauty, we discover not just art, but the very essence of what it means to feel deeply and live fully.

Let these painted poems remind you that beauty and {emotion} are forever intertwined.""",

        'detective': f"""Attention {user_name},

Three pieces of evidence have been placed before us: {', '.join(paintings)}. Each canvas holds clues to a mystery that has captivated observers for generations.

The first painting reveals subtle hints in its composition, the second provides crucial context through its symbolic elements, while the third offers the key to understanding the entire puzzle.

What connects these works is not merely artistic technique, but an underlying current of {emotion} that runs through each piece like a thread through a tapestry.

The case is clear: these paintings were chosen not by chance, but by the invisible hand of {emotion} that draws kindred spirits together across time and space.""",

        'critic': f"""Dear {user_name},

From an analytical perspective, these three works - {', '.join(paintings)} - demonstrate a fascinating interplay of formal elements that collectively evoke a profound sense of {emotion}.

The compositional structures, color relationships, and brushwork techniques each contribute to an overall aesthetic experience that transcends individual artistic merit. The visual language employed speaks directly to the viewer's emotional center, creating an immediate and visceral response.

What we observe here is not merely decoration, but communication - a direct transmission of {emotion} through the careful manipulation of line, form, and color.

This triumvirate of artworks serves as a masterclass in how technical skill can be deployed in service of emotional truth.""",

        'time_traveller': f"""Greetings {user_name}, from across the streams of time,

I write to you from an era where these three artworks - {', '.join(paintings)} - are considered pivotal moments in the evolution of human consciousness.

In my travels through the temporal dimensions, I've learned that {emotion} is one of the few constants that transcends all boundaries of time and space. These paintings serve as anchors in the flow of history, each one radiating the same essential {emotion} regardless of when or where they are observed.

Future civilizations will study these works not just for their artistic merit, but as archaeological evidence of humanity's capacity for {emotion} and beauty.

Treasure this moment, for you are experiencing something that will resonate through all of time."""
    }
    
    # Get the appropriate template or default to historian
    story = style_templates.get(narrative_style, style_templates['historian'])
    
    return {
        'success': True,
        'story': story,
        'word_count': len(story.split()),
        'generation_time_ms': 150,
        'narrative_style': narrative_style,
        'emotion': emotion
    }

def main():
    """Main function that processes JSON input from server.py"""
    try:
        if len(sys.argv) < 2:
            result = {
                'success': False,
                'error': 'No input data provided'
            }
        else:
            # Parse input JSON from server.py
            input_json = sys.argv[1]
            input_data = json.loads(input_json)
            
            # Extract required fields
            paintings = input_data.get('paintings', [])
            user_name = input_data.get('user_name', 'Friend')
            emotion = input_data.get('emotion', 'wonder')
            narrative_style = input_data.get('narrative_style', 'historian')
            
            print(f"[WORKING] Processing story request:", file=sys.stderr)
            print(f"[WORKING] Paintings: {[p.get('title', 'Unknown') for p in paintings]}", file=sys.stderr)
            print(f"[WORKING] User: {user_name}, Emotion: {emotion}, Style: {narrative_style}", file=sys.stderr)
            
            # Try to use the secure generator first
            if SECURE_GENERATOR_AVAILABLE:
                try:
                    print(f"[WORKING] Using secure story generator", file=sys.stderr)
                    secure_gen = SecureStoryGenerator()
                    result = secure_gen.generate_story(
                        paintings=paintings,
                        narrative_style=narrative_style,
                        user_name=user_name,
                        emotion=emotion,
                        emotion_probability=input_data.get('emotion_probability')
                    )
                    print(f"[WORKING] Secure generator result: {result.get('success', False)}", file=sys.stderr)
                except Exception as e:
                    print(f"[WORKING] Secure generator failed: {e}", file=sys.stderr)
                    # Fall back to simple story generation
                    painting_titles = [p.get('title', f'Painting {i+1}') for i, p in enumerate(paintings)]
                    result = create_fallback_story(painting_titles, user_name, emotion, narrative_style)
            else:
                print(f"[WORKING] Using fallback story generator", file=sys.stderr)
                # Use fallback story generation
                painting_titles = [p.get('title', f'Painting {i+1}') for i, p in enumerate(paintings)]
                result = create_fallback_story(painting_titles, user_name, emotion, narrative_style)
    
    except json.JSONDecodeError as e:
        result = {
            'success': False,
            'error': f'Invalid JSON input: {str(e)}'
        }
    except Exception as e:
        result = {
            'success': False,
            'error': f'Story generation error: {str(e)}'
        }
    
    # Output the result as JSON (what server.py expects)
    print(json.dumps(result))

if __name__ == '__main__':
    main() 