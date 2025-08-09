#!/usr/bin/env python3
"""
Secure wrapper for story generation with API usage restrictions
This ensures the OpenAI API is ONLY used for story generation
"""

import json
import sys
import os
from datetime import datetime
from image_story_generator import ImageStoryGenerator  # Import the new image-based generator

class SecureStoryGenerator:
    """Wrapper class with additional security and usage restrictions"""
    
    def __init__(self):
        self.generator = ImageStoryGenerator()  # Use image-based generator (OpenAI-backed)
        self.allowed_operations = ['generate_story']
        self.usage_log_file = 'api_usage_log.json'
        # Safety: surface a clear warning if the OpenAI key is missing in this process
        try:
            if not os.getenv('OPENAI_API_KEY'):
                print("[SECURE] WARNING: OPENAI_API_KEY is not set in environment", file=sys.stderr)
        except Exception:
            pass
        
    def generate_story(self, paintings, narrative_style, nickname=None, emotion=None, emotion_probability=None):
        """
        Generate story with additional validation and logging
        """
        # Validate this is a legitimate story generation request
        if not self._validate_request(paintings, narrative_style):
            return {
                'success': False,
                'error': 'Invalid story generation request'
            }
        
        # Debug: Log what we received
        print(f"[DEBUG] Received {len(paintings)} paintings", file=sys.stderr)
        if emotion and emotion_probability is not None:
            print(f"[DEBUG] Emotion data: {emotion} ({emotion_probability}%)", file=sys.stderr)
        
        # Log the request
        self._log_request('generate_story', {
            'paintings': [{'title': p.get('title'), 'artist': p.get('artist')} for p in paintings],
            'narrative_style': narrative_style,
            'nickname': nickname,
            'emotion': emotion,
            'emotion_probability': emotion_probability,
            'timestamp': datetime.now().isoformat(),
            'with_images': True
        })
        
        # Call the actual story generator
        print(f"[SECURE] Authorized story generation request", file=sys.stderr)
        if nickname:
            print(f"[SECURE] Nickname: {nickname}", file=sys.stderr)
        if emotion and emotion_probability is not None:
            print(f"[SECURE] With emotion: {emotion} ({emotion_probability}%)", file=sys.stderr)
        result = self.generator.generate_story(paintings, narrative_style, nickname, emotion, emotion_probability)
        
        # Log the result
        self._log_result(result)
        
        return result
    
    def _validate_request(self, paintings, narrative_style):
        """Validate that this is a legitimate story generation request"""
        # Check paintings
        if not isinstance(paintings, list) or len(paintings) != 3:
            print("[SECURE] Validation failed: Invalid paintings", file=sys.stderr)
            return False
            
        for i, painting in enumerate(paintings):
            # Check required fields
            required_fields = ['title', 'artist']
            missing_fields = [field for field in required_fields if field not in painting]
            if missing_fields:
                print(f"[SECURE] Validation failed: Missing painting {i+1} information. Missing fields: {missing_fields}", file=sys.stderr)
                return False
            
            # Check image path exists - REQUIRED for story generation
            if 'imagePath' not in painting:
                print(f"[SECURE] Validation failed: Missing image path for painting {i+1}", file=sys.stderr)
                return False
                
            if not os.path.exists(painting['imagePath']):
                print(f"[SECURE] Validation failed: Image file not found for painting {i+1}: {painting['imagePath']}", file=sys.stderr)
                return False
        
        # Check narrative style
        valid_styles = ['historian', 'poet', 'detective', 'critic', 'time_traveller']
        if narrative_style not in valid_styles:
            print("[SECURE] Validation failed: Invalid narrative style", file=sys.stderr)
            return False
            
        return True
    
    def _log_request(self, operation, details):
        """Log API usage requests"""
        log_entry = {
            'operation': operation,
            'timestamp': datetime.now().isoformat(),
            'details': details
        }
        
        # Load existing log
        try:
            with open(self.usage_log_file, 'r') as f:
                log = json.load(f)
        except:
            log = []
        
        # Add new entry
        log.append(log_entry)
        
        # Save log
        with open(self.usage_log_file, 'w') as f:
            json.dump(log, f, indent=2)
    
    def _log_result(self, result):
        """Log the result of API call"""
        if result.get('success'):
            print(f"[SECURE] Story generated successfully", file=sys.stderr)
        else:
            print(f"[SECURE] Story generation failed: {result.get('error')}", file=sys.stderr)
    
    def get_usage_stats(self):
        """Get API usage statistics"""
        stats = self.generator.get_api_usage_stats()
        print(f"\n[SECURE] API Usage Statistics:", file=sys.stderr)
        print(f"  Total API calls: {stats['total_api_calls']}", file=sys.stderr)
        print(f"  Client initialized: {stats['client_initialized']}", file=sys.stderr)
        return stats

def main():
    """Main function for secure story generation"""
    if len(sys.argv) < 2:
        print("Usage: python secure_story_generator.py '<json_input>'", file=sys.stderr)
        sys.exit(1)
    
    try:
        # Parse input
        input_data = json.loads(sys.argv[1])
        
        # Map data from generate-story endpoint format
        paintings = input_data.get('paintings', [])
        narrative_style = input_data.get('character', '')  # character maps to narrative_style
        nickname = input_data.get('nickname', '')
        emotion = input_data.get('emotion', None)
        emotion_probability = input_data.get('emotion_probability', None)
        
        print(f"[SECURE] Mapped data - paintings: {len(paintings)}, narrative_style: {narrative_style}, nickname: {nickname}", file=sys.stderr)
        print(f"[SECURE] Emotion: {emotion} ({emotion_probability}%)", file=sys.stderr)
        
        # Create secure generator
        secure_gen = SecureStoryGenerator()
        
        # Generate story
        result = secure_gen.generate_story(
            paintings=paintings,
            narrative_style=narrative_style,
            nickname=nickname,
            emotion=emotion,
            emotion_probability=emotion_probability
        )
        
        # Output result to stdout (clean JSON only)
        print(json.dumps(result, indent=2))
        
        # Show usage stats to stderr
        secure_gen.get_usage_stats()
        
    except Exception as e:
        error_result = {
            'success': False,
            'error': str(e)
        }
        print(json.dumps(error_result, indent=2))
        sys.exit(1)

if __name__ == "__main__":
    main() 