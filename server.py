#!/usr/bin/env python3

import os
import json
import uuid
import asyncio
import subprocess
import requests
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import tempfile
import signal
import sys
import time
from PIL import Image
import colorsys

from flask import Flask, request, jsonify, send_from_directory, send_file, Response
from flask_cors import CORS
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Now you can securely access your variables using os.getenv()
db_password = os.getenv('DATABASE_PASSWORD')
gcp_credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

# Import database after app creation
try:
    from database import db
    DB_ENABLED = True
    logger.info("Database integration enabled")
except ImportError as e:
    logger.warning(f"Database not available: {e}")
    DB_ENABLED = False

# Configuration
PORT = int(os.environ.get('PORT', 3000))
# Use absolute path to avoid any ambiguity with working directory
UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', '/app/uploads')
PUBLIC_FOLDER = 'public'
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Session storage (in production, use Redis or database)
session_storage = {}

# Ensure directories exist
def ensure_directory_exists(directory: str):
    Path(directory).mkdir(parents=True, exist_ok=True)

ensure_directory_exists(UPLOAD_FOLDER)
ensure_directory_exists(PUBLIC_FOLDER)

# Configure Flask upload settings
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Helper functions
def generate_session_id() -> str:
    """Generate unique session ID"""
    return str(uuid.uuid4())

def get_or_create_session(request_data: dict = None) -> str:
    """Get existing session ID or create new one"""
    session_id = None
    
    # Try to get from headers first
    if hasattr(request, 'headers'):
        session_id = request.headers.get('X-Session-ID')
    
    # Try to get from request data
    if not session_id and request_data:
        session_id = request_data.get('sessionId')
    
    # Create new session if none exists
    if not session_id:
        session_id = generate_session_id()
        logger.info(f"🆕 Created new session: {session_id}")
    
    # Initialize session storage if not exists
    if session_id not in session_storage:
        session_storage[session_id] = {
            'created_at': datetime.now().isoformat(),
            'user_info': {},
            'captured_palette': None,
            'selected_emotion': None,
            'selected_paintings': [],
            'story_data': None
        }
    
    return session_id

def allowed_file(filename: str) -> bool:
    """Check if file type is allowed"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_unique_filename() -> str:
    """Generate unique filename for uploaded palette"""
    timestamp = int(datetime.now().timestamp() * 1000)
    unique_id = str(uuid.uuid4())
    return f"palette-{timestamp}-{unique_id}.png"

def download_image(url: str, filename: str) -> str:
    """Download image from URL and save to uploads folder"""
    try:
        # Include headers to comply with Wikimedia policy and improve compatibility
        headers = {
            'User-Agent': 'PlotPaletteBot/1.0 (https://plotpalette.example.com/; contact@plotpalette.example.com) Educational-Research-Tool',
            'Accept': 'image/*,*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        response = requests.get(url, headers=headers, timeout=30, stream=True, verify=True)
        response.raise_for_status()
        
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        with open(file_path, 'wb') as f:
            shutil.copyfileobj(response.raw, f)
        
        return file_path
    except Exception as e:
        logger.error(f"Failed to download image {url}: {e}")
        raise

def run_emotion_prediction_service(image_path: str) -> Dict[str, Any]:
    """Run emotion prediction service and parse output"""
    try:
        # Use the emotion prediction script in the emotions_generation container
        script_path = os.path.join(os.getcwd(), 'emotions_generation', 'emotion_prediction.py')
        
        # Use virtual environment Python if available, otherwise fall back to system Python
        venv_python = os.path.join(os.getcwd(), 'venv', 'bin', 'python3')
        if os.path.exists(venv_python):
            python_executable = venv_python
        else:
            python_executable = 'python3'
        
        args = [python_executable, script_path, image_path]
        
        logger.info(f"Running emotion prediction service: {' '.join(args)}")
        
        result = subprocess.run(
            args,
            cwd=os.getcwd(),
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode != 0:
            logger.error(f"Emotion prediction service error: {result.stderr}")
            raise Exception(f"Emotion prediction service failed with code {result.returncode}: {result.stderr}")
        
        logger.info("Emotion prediction service completed successfully")
        
        # Parse the output to extract emotion prediction and raw colors
        parsed_result = parse_emotion_prediction_output(result.stdout)
        return parsed_result
        
    except Exception as e:
        logger.error(f"Error running emotion prediction service: {e}")
        raise

def run_recommendation_service(raw_colors_json: str) -> Dict[str, Any]:
    """Run recommendation service with raw colors and parse output"""
    try:
        # Use the recommendation script in the painting_recommendation folder
        script_path = os.path.join(os.getcwd(), 'painting_recommendation', 'recommendation_service.py')
        
        # Use virtual environment Python if available, otherwise fall back to system Python
        venv_python = os.path.join(os.getcwd(), 'venv', 'bin', 'python3')
        if os.path.exists(venv_python):
            python_executable = venv_python
        else:
            python_executable = 'python3'
        
        args = [python_executable, script_path, raw_colors_json]
        
        logger.info(f"Running recommendation service: {' '.join(args[:2])} [raw_colors_json]")
        
        result = subprocess.run(
            args,
            cwd=os.getcwd(),
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode != 0:
            logger.error(f"Recommendation service error: {result.stderr}")
            if result.stdout:
                logger.error(f"Recommendation service stdout: {result.stdout}")
            raise Exception(f"Recommendation service failed with code {result.returncode}: {result.stderr}")
        
        logger.info("Recommendation service completed successfully")
        
        # Parse the output to extract recommendations
        parsed_result = parse_recommendation_service_output(result.stdout)
        return parsed_result
        
    except Exception as e:
        logger.error(f"Error running recommendation service: {e}")
        raise

def _rgb_tuple_from_color_obj(color_obj: Dict[str, Any]) -> Optional[tuple]:
    try:
        if isinstance(color_obj, dict):
            if all(k in color_obj for k in ('r','g','b')):
                return (int(color_obj['r']), int(color_obj['g']), int(color_obj['b']))
            if 'hex' in color_obj:
                h = str(color_obj['hex']).lstrip('#')
                if len(h) == 3:
                    h = ''.join([c*2 for c in h])
                r = int(h[0:2], 16)
                g = int(h[2:4], 16)
                b = int(h[4:6], 16)
                return (r,g,b)
            if 'color' in color_obj:
                h = str(color_obj['color']).lstrip('#')
                if len(h) == 3:
                    h = ''.join([c*2 for c in h])
                r = int(h[0:2], 16)
                g = int(h[2:4], 16)
                b = int(h[4:6], 16)
                return (r,g,b)
    except Exception:
        return None
    return None

def _enrich_raw_color(color_obj: Dict[str, Any]) -> Dict[str, Any]:
    # If already enriched, return as-is
    if isinstance(color_obj, dict) and ('bgr' in color_obj and 'hsv' in color_obj and 'lab' in color_obj):
        return color_obj
    # Determine RGB
    rgb = _rgb_tuple_from_color_obj(color_obj)
    if not rgb:
        # Fallback to black
        rgb = (0,0,0)
    r,g,b = rgb
    # Build BGR
    bgr = [b, g, r]
    # HSV using colorsys scaled to OpenCV-like ranges (H:0-180, S:0-255, V:0-255)
    h, s, v = colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)
    hsv = [int(round(h*180)), int(round(s*255)), int(round(v*255))]
    # LAB using Pillow conversion
    try:
        img = Image.new('RGB', (1,1), (r,g,b)).convert('LAB')
        L, A, B = img.getpixel((0,0))
        lab = [int(L), int(A), int(B)]
    except Exception:
        lab = [0, 128, 128]
    percentage = color_obj.get('percentage', 0.2) if isinstance(color_obj, dict) else 0.2
    return {
        'bgr': bgr,
        'hsv': hsv,
        'lab': lab,
        'percentage': float(percentage)
    }

def ensure_enriched_raw_colors(raw_colors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not isinstance(raw_colors, list):
        return []
    if len(raw_colors) == 5 and all(isinstance(c, dict) and ('bgr' in c and 'hsv' in c and 'lab' in c) for c in raw_colors):
        return raw_colors
    enriched = [_enrich_raw_color(c) for c in raw_colors[:5]]
    # Normalize percentages if missing or not summing to 1.0
    total = sum(c.get('percentage', 0) for c in enriched)
    if total <= 0:
        for c in enriched:
            c['percentage'] = 1.0/len(enriched)
    else:
        for c in enriched:
            c['percentage'] = float(c.get('percentage', 0))/total
    return enriched

def run_python_script(script_path: str, image_path: str = None) -> Dict[str, Any]:
    """Legacy function - now runs both services sequentially"""
    try:
        logger.info("Running separated emotion prediction and recommendation services...")
        
        # Step 1: Run emotion prediction service
        emotion_result = run_emotion_prediction_service(image_path)
        
        # Step 2: Run recommendation service with raw colors from emotion prediction
        raw_colors_json = json.dumps(emotion_result['rawColors'])
        recommendation_result = run_recommendation_service(raw_colors_json)
        
        # Combine results
        combined_result = {
            'urls': recommendation_result['urls'],
            'colourData': emotion_result['colourData'],
            'rawColors': emotion_result['rawColorsForFrontend'],
            'detailedRecommendations': recommendation_result['detailedRecommendations'],
            'emotionPrediction': emotion_result['emotionPrediction']
        }
        
        return combined_result
        
    except Exception as e:
        logger.error(f"Error running separated services: {e}")
        raise

def parse_emotion_prediction_output(output: str) -> Dict[str, Any]:
    """Parse emotion prediction service output"""
    colour_data = {}
    raw_colors = []
    raw_colors_for_frontend = {}
    emotion_prediction = None
    
    lines = output.split('\n')
    
    # Parse mapped colour percentages
    for line in lines:
        # Parse colour percentage lines like "  black: 0.5302"
        import re
        colour_match = re.match(r'^\s+([a-z]+):\s+([\d.]+)$', line)
        if colour_match:
            colour_name = colour_match.group(1)
            percentage = float(colour_match.group(2))
            colour_data[colour_name] = percentage
        
        # Parse raw RGB colors from the new format: "  Raw Color 1: RGB(139, 84, 181) - 10.27%"
        raw_color_match = re.search(r'\s*Raw Color \d+: RGB\((\d+), (\d+), (\d+)\) - ([\d.]+)%', line)
        if raw_color_match:
            r = int(raw_color_match.group(1))
            g = int(raw_color_match.group(2))
            b = int(raw_color_match.group(3))
            percentage = float(raw_color_match.group(4)) / 100  # Convert percentage to decimal
            
            # Convert RGB to hex for frontend
            hex_color = f"#{r:02x}{g:02x}{b:02x}"
            
            # Store as hex-color: percentage mapping for frontend
            raw_colors_for_frontend[hex_color] = percentage
            logger.info(f"🎨 Parsed raw color: RGB({r}, {g}, {b}) = {hex_color} ({percentage*100:.2f}%)")
    
    # Parse raw colors JSON
    raw_colors_start_index = output.find('--- RAW_COLORS_JSON ---')
    raw_colors_end_index = output.find('--- END_RAW_COLORS_JSON ---')
    
    if raw_colors_start_index != -1 and raw_colors_end_index != -1:
        raw_colors_json_str = output[
            raw_colors_start_index + len('--- RAW_COLORS_JSON ---'):
            raw_colors_end_index
        ].strip()
        
        try:
            raw_colors = json.loads(raw_colors_json_str)
            logger.info(f"Parsed {len(raw_colors)} raw colors for recommendation service")
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing raw colors JSON: {e}")
            raw_colors = []
    
    # Parse emotion prediction JSON
    emotion_start_index = output.find('--- EMOTION_PREDICTION_JSON ---')
    emotion_end_index = output.find('--- END_EMOTION_PREDICTION_JSON ---')
    
    if emotion_start_index != -1 and emotion_end_index != -1:
        emotion_json_str = output[
            emotion_start_index + len('--- EMOTION_PREDICTION_JSON ---'):
            emotion_end_index
        ].strip()
        
        try:
            emotion_prediction = json.loads(emotion_json_str)
            logger.info(f"Parsed emotion prediction: {emotion_prediction['emotion']} ({emotion_prediction['confidence_percentage']})")
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing emotion prediction JSON: {e}")
            emotion_prediction = {
                'emotion': 'unknown',
                'confidence_percentage': '0%',
                'all_probabilities': {}
            }
    else:
        # Fallback: create default emotion prediction
        emotion_prediction = {
            'emotion': 'unknown',
            'confidence_percentage': '0%',
            'all_probabilities': {}
        }
    
    return {
        'colourData': colour_data,
        'rawColors': raw_colors,
        'rawColorsForFrontend': raw_colors_for_frontend,
        'emotionPrediction': emotion_prediction
    }

def parse_recommendation_service_output(output: str) -> Dict[str, Any]:
    """Parse recommendation service output"""
    urls = []
    detailed_recommendations = []
    
    lines = output.split('\n')
    
    # Parse URLs
    in_recommendation_section = False
    for line in lines:
        # Look for the section with recommendations
        if 'Top 10 Recommended Painting URLs' in line:
            in_recommendation_section = True
            continue
        
        if in_recommendation_section:
            # Look for numbered lines with URLs
            import re
            match = re.match(r'^\d+\.\s+(.+)$', line)
            if match:
                url = match.group(1).strip()
                if url and url.startswith('http'):
                    urls.append(url)
        
        # Stop if we've found URLs and hit an empty line or other content
        if in_recommendation_section and len(urls) > 0 and line.strip() == '':
            break
    
    # Parse detailed recommendations JSON
    json_start_index = output.find('--- DETAILED_RECOMMENDATIONS_JSON ---')
    json_end_index = output.find('--- END_DETAILED_RECOMMENDATIONS_JSON ---')
    
    if json_start_index != -1 and json_end_index != -1:
        json_str = output[
            json_start_index + len('--- DETAILED_RECOMMENDATIONS_JSON ---'):
            json_end_index
        ].strip()
        
        try:
            detailed_recommendations = json.loads(json_str)
            logger.info(f"Parsed {len(detailed_recommendations)} detailed recommendations")
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing detailed recommendations JSON: {e}")
            # Fallback: create basic objects from URLs
            detailed_recommendations = [
                {
                    'url': url,
                    'page': '',
                    'title': f'Painting {index + 1}',
                    'artist': 'Unknown Artist'
                }
                for index, url in enumerate(urls)
            ]
    else:
        # Fallback: create basic objects from URLs
        detailed_recommendations = [
            {
                'url': url,
                'page': '',
                'title': f'Painting {index + 1}',
                'artist': 'Unknown Artist'
            }
            for index, url in enumerate(urls)
        ]
    
    return {
        'urls': urls,
        'detailedRecommendations': detailed_recommendations
    }

def parse_recommendation_output(output: str) -> Dict[str, Any]:
    """Parse Python script output and extract URLs, colour data, and detailed recommendations"""
    urls = []
    lines = output.split('\n')
    
    in_recommendation_section = False
    colour_data = {}
    raw_color_data = {}
    detailed_recommendations = []
    emotion_prediction = None
    
    # Parse raw extracted colors and mapped colour percentages
    for line in lines:
        # Parse raw RGB colors from the new format: "  Raw Color 1: RGB(139, 84, 181) - 10.27%"
        import re
        raw_color_match = re.search(r'\s*Raw Color \d+: RGB\((\d+), (\d+), (\d+)\) - ([\d.]+)%', line)
        if raw_color_match:
            r = int(raw_color_match.group(1))
            g = int(raw_color_match.group(2))
            b = int(raw_color_match.group(3))
            percentage = float(raw_color_match.group(4)) / 100  # Convert percentage to decimal
            
            # Convert RGB to hex for frontend
            hex_color = f"#{r:02x}{g:02x}{b:02x}"
            
            # Store as hex-color: percentage mapping (same format as colourData)
            raw_color_data[hex_color] = percentage
            logger.info(f"🎨 Parsed raw color: RGB({r}, {g}, {b}) = {hex_color} ({percentage*100:.2f}%)")
        
        # Also parse old format for backwards compatibility
        old_raw_color_match = re.search(r'Analyzing extracted color: RGB\(.*?(\d+).*?(\d+).*?(\d+)\)', line)
        if old_raw_color_match and len(raw_color_data) == 0:  # Only use if new format not found
            r = int(old_raw_color_match.group(1))
            g = int(old_raw_color_match.group(2))
            b = int(old_raw_color_match.group(3))
            hex_color = f"#{r:02x}{g:02x}{b:02x}"
            # Store as hex-color: percentage mapping (default equal distribution)
            raw_color_data[hex_color] = 1.0 / 5  # Default equal percentage
        
        if 'Final colour selection:' in line:
            # Start parsing colour data from the next lines
            continue
        
        # Parse colour percentage lines like "  black: 0.5302"
        colour_match = re.match(r'^\s+([a-z]+):\s+([\d.]+)$', line)
        if colour_match:
            colour_name = colour_match.group(1)
            percentage = float(colour_match.group(2))
            colour_data[colour_name] = percentage
        
        # Look for the section with recommendations
        if 'Top 10 Recommended Painting URLs' in line:
            in_recommendation_section = True
            continue
        
        if in_recommendation_section:
            # Look for numbered lines with URLs
            match = re.match(r'^\d+\.\s+(.+)$', line)
            if match:
                url = match.group(1).strip()
                if url and url.startswith('http'):
                    urls.append(url)
        
        # Stop if we've found URLs and hit an empty line or other content
        if in_recommendation_section and len(urls) > 0 and line.strip() == '':
            break
    
    # Raw colors now include percentages from the parsing above
    raw_colors = raw_color_data
    
    # Parse detailed recommendations JSON
    json_start_index = output.find('--- DETAILED_RECOMMENDATIONS_JSON ---')
    json_end_index = output.find('--- END_DETAILED_RECOMMENDATIONS_JSON ---')
    
    if json_start_index != -1 and json_end_index != -1:
        json_str = output[
            json_start_index + len('--- DETAILED_RECOMMENDATIONS_JSON ---'):
            json_end_index
        ].strip()
        
        try:
            detailed_recommendations = json.loads(json_str)
            logger.info(f"Parsed {len(detailed_recommendations)} detailed recommendations")
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing detailed recommendations JSON: {e}")
            # Fallback: create basic objects from URLs
            detailed_recommendations = [
                {
                    'url': url,
                    'title': f'Painting {index + 1}',
                    'artist': 'Unknown Artist',
                    'year': 'Unknown Year'
                }
                for index, url in enumerate(urls)
            ]
    else:
        # Fallback: create basic objects from URLs
        detailed_recommendations = [
            {
                'url': url,
                'title': f'Painting {index + 1}',
                'artist': 'Unknown Artist',
                'year': 'Unknown Year'
            }
            for index, url in enumerate(urls)
        ]
    
    # Parse emotion prediction JSON
    emotion_start_index = output.find('--- EMOTION_PREDICTION_JSON ---')
    emotion_end_index = output.find('--- END_EMOTION_PREDICTION_JSON ---')
    
    if emotion_start_index != -1 and emotion_end_index != -1:
        emotion_json_str = output[
            emotion_start_index + len('--- EMOTION_PREDICTION_JSON ---'):
            emotion_end_index
        ].strip()
        
        try:
            emotion_prediction = json.loads(emotion_json_str)
            logger.info(f"Parsed emotion prediction: {emotion_prediction['emotion']} ({emotion_prediction['confidence_percentage']})")
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing emotion prediction JSON: {e}")
            emotion_prediction = {
                'emotion': 'unknown',
                'confidence_percentage': '0%',
                'all_probabilities': {}
            }
    else:
        # Fallback: create default emotion prediction
        emotion_prediction = {
            'emotion': 'unknown',
            'confidence_percentage': '0%',
            'all_probabilities': {}
        }
    
    return {
        'urls': urls,
        'colourData': colour_data,
        'rawColors': raw_colors,
        'detailedRecommendations': detailed_recommendations,
        'emotionPrediction': emotion_prediction
    }

# Story generation is now handled by the story-api microservice
# The run_python_story_script function has been removed in favor of HTTP API calls

# Routes

@app.route('/status')
def status_check():
    """A simple status endpoint."""
    return jsonify({'status': 'running'}), 200

@app.route('/username-check', methods=['POST'])
def username_check():
    """Check if a username exists in the database"""
    try:
        data = request.get_json() or {}
        username = data.get('username', '').strip()
        
        if not username:
            return jsonify({
                'success': False,
                'username_exist': False,
                'message': 'Username is required'
            }), 400
        
        logger.info(f"🔍 Checking username existence: {username}")
        
        # Check if username exists in database
        username_exists = False
        if DB_ENABLED:
            try:
                # Query database to check if username exists
                username_exists = db.check_username_exists(username)
                logger.info(f"📊 Database check result for '{username}': {username_exists}")
            except Exception as e:
                logger.error(f"❌ Database error checking username: {e}")
                return jsonify({
                    'success': False,
                    'username_exist': False,
                    'message': 'Database error occurred'
                }), 500
        else:
            logger.warning("⚠️ Database not enabled, cannot verify username")
            return jsonify({
                'success': False,
                'username_exist': False,
                'message': 'Database not available'
            }), 503
        
        return jsonify({
            'success': True,
            'username_exist': username_exists,
            'username': username,
            'message': f'Username {"exists" if username_exists else "not found"} in database'
        })
        
    except Exception as e:
        logger.error(f"Error checking username: {e}")
        return jsonify({
            'success': False,
            'username_exist': False,
            'message': str(e)
        }), 500

@app.route('/test-raw-colors', methods=['GET'])
def test_raw_colors():
    """Test endpoint for raw colors generation"""
    try:
        import random
        palette_colors = [
            '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8'
        ]
        selected_colors = random.sample(palette_colors, 3)
        
        raw_colors_rgb = []
        for color in selected_colors:
            hex_color = color.lstrip('#')
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16) 
            b = int(hex_color[4:6], 16)
            raw_colors_rgb.append({
                'r': r, 'g': g, 'b': b, 
                'hex': color,
                'percentage': 1.0 / len(selected_colors)
            })
        
        return jsonify({
            'success': True,
            'selectedColors': selected_colors,
            'rawColors': raw_colors_rgb
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Global username storage (persists across all sessions for a user)
username_storage = {}

@app.route('/store-username', methods=['POST'])
def store_username():
    """Store username information without creating session"""
    try:
        data = request.get_json() or {}
        
        # Extract user information
        username = data.get('name', '')
        age = data.get('age', '')
        gender = data.get('gender', '')
        fieldOfStudy = data.get('fieldOfStudy', '')
        frequency = data.get('frequency', '')
        
        # Store username globally (persists across sessions)
        if username:
            username_storage[username] = {
                'created_at': datetime.now().isoformat(),
                'user_info': {
                    'name': username,
                    'age': age,
                    'gender': gender,
                    'fieldOfStudy': fieldOfStudy,
                    'frequency': frequency
                }
            }
        
        # Save to database if available
        if DB_ENABLED and username:
            try:
                db.save_user_info(
                    username=username,
                    age=age,
                    gender=gender,
                    fieldOfStudy=fieldOfStudy,
                    frequency=frequency
                )
                logger.info(f"✅ User info saved to database for username: {username}")
            except Exception as e:
                logger.error(f"❌ Failed to save user info to database: {e}")
        
        logger.info(f"👤 Stored username: {username} with info: age={age}, gender={gender}, field={fieldOfStudy}, frequency={frequency}")
        return jsonify({
            'success': True,
            'username': username,
            'message': 'Username stored successfully'
        })
        
    except Exception as e:
        logger.error(f"Error storing username: {e}")
        return jsonify({
            'error': 'Failed to store username',
            'message': str(e)
        }), 500

@app.route('/create-session', methods=['POST'])
def create_session():
    """Create a new session with existing username"""
    try:
        data = request.get_json() or {}
        session_id = generate_session_id()
        
        # Get username from data or storage
        username = data.get('username', '')
        user_info = {}
        
        if username and username in username_storage:
            user_info = username_storage[username]['user_info']
            logger.info(f"🔗 Linking session {session_id} to existing username: {username}")
        else:
            logger.info(f"🆕 Creating session {session_id} without existing username")
        
        # Create session storage
        session_storage[session_id] = {
            'created_at': datetime.now().isoformat(),
            'username': username,
            'user_info': user_info,
            'captured_palette': None,
            'selected_emotion': None,
            'selected_paintings': [],
            'story_data': None
        }
        
        # Save to database if available and username exists
        if DB_ENABLED and username:
            try:
                db.create_session(username=username, session_id=session_id)
                logger.info(f"✅ Session created in database: {session_id} for username: {username}")
            except Exception as e:
                logger.error(f"❌ Failed to create session in database: {e}")
        
        return jsonify({
            'success': True,
            'sessionId': session_id,
            'username': username,
            'message': 'Session created successfully'
        })
        
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        return jsonify({
            'error': 'Failed to create session',
            'message': str(e)
        }), 500

@app.route('/capture-gif-frame', methods=['POST'])
def capture_gif_frame():
    """Capture a specific frame from a GIF and save it as an image"""
    try:
        data = request.get_json() or {}
        gif_name = data.get('gifName', '1.gif')
        frame_number = data.get('frameNumber', 0)  # Which frame to capture
        
        logger.info(f"🎬 Capturing frame {frame_number} from GIF: {gif_name}")
        
        # Look for the GIF in the palette GIF folder
        gif_path = os.path.join('palette GIF', gif_name)
        
        if not os.path.exists(gif_path):
            # Try alternative path
            gif_path = os.path.join('frontend-vue/src/assets/images/palette GIF', gif_name)
        
        if not os.path.exists(gif_path):
            raise FileNotFoundError(f"GIF file not found: {gif_name}")
        
        # Use PIL to capture the specific frame
        from PIL import Image
        
        with Image.open(gif_path) as gif:
            # Seek to the specific frame
            if hasattr(gif, 'n_frames') and frame_number < gif.n_frames:
                gif.seek(frame_number)
            else:
                # If frame_number is out of range, use the current frame
                gif.seek(0)
            
            # Convert to RGB if necessary
            frame = gif.convert('RGB')
            
            # Generate unique filename for captured frame
            filename = generate_unique_filename()
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # Save the captured frame
            frame.save(file_path, 'PNG', quality=95)
            
            logger.info(f"✅ GIF frame captured and saved: {filename}")
            
            return jsonify({
                'success': True,
                'filename': filename,
                'gifName': gif_name,
                'frameNumber': frame_number,
                'message': f'Frame {frame_number} captured from {gif_name}'
            })
    
    except Exception as e:
        logger.error(f"❌ Error capturing GIF frame: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/capture-palette', methods=['POST'])
def capture_palette():
    """Capture and analyze palette - with real GIF frame capture"""
    try:
        data = request.get_json() or {}
        session_id = get_or_create_session(data)
        
        gif_name = data.get('gifName', '1.gif')
        frame_data = data.get('frameData')  # Base64 encoded frame data from frontend
        
        filename = generate_unique_filename()
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        if frame_data:
            # Use the actual captured frame from frontend
            import base64
            from io import BytesIO
            
            # Remove data URL prefix if present
            if frame_data.startswith('data:image'):
                frame_data = frame_data.split(',')[1]
            
            # Decode and save the image
            image_data = base64.b64decode(frame_data)
            
            with open(file_path, 'wb') as f:
                f.write(image_data)
            
            logger.info(f"🖼️ Saved captured frame from frontend: {filename}")
        else:
            # Fallback: Create a dummy palette image with multiple colors (for testing)
            logger.info(f"⚠️ No frame data received, creating dummy palette for: {gif_name}")
            
            import random
            from PIL import Image, ImageDraw
            
            palette_colors = [
                '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8',
                '#F7DC6F', '#BB8FCE', '#85C1E9', '#F8C471', '#82E0AA'
            ]
            selected_colors = random.sample(palette_colors, 5)
            
            # Create image with color bands to simulate real palette
            img = Image.new('RGB', (600, 400), '#000000')
            draw = ImageDraw.Draw(img)
            
            # Draw color bands
            band_width = 600 // len(selected_colors)
            for i, color in enumerate(selected_colors):
                # Convert hex to RGB
                hex_color = color.lstrip('#')
                rgb_color = tuple(int(hex_color[j:j+2], 16) for j in (0, 2, 4))
                
                x1 = i * band_width
                x2 = (i + 1) * band_width if i < len(selected_colors) - 1 else 600
                draw.rectangle([x1, 0, x2, 400], fill=rgb_color)
            
            img.save(file_path)
        
        # Store palette info in session
        session_storage[session_id]['captured_palette'] = {
            'filename': filename,
            'gifName': gif_name,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"🎨 Running palette analysis for {filename}")
        
        # Run the Python recommendation script
        result = run_python_script(None, file_path)
        
        # Always use raw colors from Python script output if available
        script_raw_colors = result.get('rawColors', [])
        if script_raw_colors and len(script_raw_colors) > 0:
            final_raw_colors = script_raw_colors
            logger.info(f"📝 Using raw colors from Python script: {len(script_raw_colors)} colors")
        else:
            # Fallback: create raw colors from dummy data
            final_raw_colors = []
            logger.info(f"📝 No raw colors from script, using empty array")
        
        # Update result to ensure rawColors is set
        result['rawColors'] = final_raw_colors
        logger.info(f"📝 Final raw colors for frontend: {len(final_raw_colors)} colors")
        
        # Save complete metadata file for session-palette endpoint
        metadata_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{Path(filename).stem}.json")
        metadata = {
            'filename': filename,
            'gifName': gif_name,
            'timestamp': datetime.now().isoformat(),
            'sessionId': session_id,
            'colourData': result.get('colourData', {}),
            'rawColors': final_raw_colors,
            'emotionPrediction': result.get('emotionPrediction', {}),
            'detailedRecommendations': result.get('detailedRecommendations', []),
            'urls': result.get('urls', [])
        }
        
        try:
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            logger.info(f"✅ Saved metadata file: {metadata_path}")
        except Exception as e:
            logger.error(f"❌ Failed to save metadata file: {e}")
        
        # Save palette analysis and recommendations to database if available
        if DB_ENABLED:
            # Save palette analysis (emotion scores) - separate try-catch
            try:
                emotion_data = result.get('emotionPrediction', {})
                all_probabilities = emotion_data.get('all_probabilities', {})
                
                db.save_palette_analyse(
                    session_id=session_id,
                    gifname=gif_name,
                    emotion_scores=all_probabilities
                )
                logger.info(f"✅ Palette analysis saved to database for session: {session_id}")
            except Exception as e:
                logger.error(f"❌ Failed to save palette analysis to database: {e}")
            
            # Save painting recommendations - separate try-catch
            try:
                painting_urls = result.get('urls', [])[:10]
                
                # Debug logging for painting recommendations
                logger.info(f"🔍 DEBUG: Full result keys: {list(result.keys())}")
                logger.info(f"🔍 DEBUG: result.get('urls'): {result.get('urls', 'NOT_FOUND')}")
                logger.info(f"🔍 DEBUG: result.get('recommendations'): {result.get('recommendations', 'NOT_FOUND')}")
                logger.info(f"🔍 DEBUG: result.get('detailedRecommendations'): {len(result.get('detailedRecommendations', [])) if result.get('detailedRecommendations') else 'NOT_FOUND'}")
                logger.info(f"🔍 DEBUG: painting_urls length: {len(painting_urls)}")
                logger.info(f"🔍 DEBUG: first 3 painting_urls: {painting_urls[:3] if painting_urls else 'EMPTY'}")
                
                db.save_painting_recommendations(
                    session_id=session_id,
                    urls=painting_urls
                )
                logger.info(f"✅ Painting recommendations saved to database for session: {session_id}")
            except Exception as e:
                logger.error(f"❌ Failed to save painting recommendations to database: {e}")
        
        return jsonify({
            'success': True,
            'sessionId': session_id,
            'filename': filename,
            'gifName': gif_name,
            'colors': result.get('urls', []),  # Keep for compatibility
            'recommendations': result.get('urls', []),
            'colourData': result.get('colourData', {}),
            'rawColors': final_raw_colors,
            'detailedRecommendations': result.get('detailedRecommendations', []),
            'emotionPrediction': result.get('emotionPrediction', {}),
            'total': len(result.get('urls', []))
        })
        
    except Exception as e:
        logger.error(f"Error capturing palette: {e}")
        return jsonify({
            'error': 'Failed to capture palette',
            'message': str(e)
        }), 500

@app.route('/')
def index():
    """Serve the main index.html file"""
    return send_file('index.html')

@app.route('/favicon.ico')
def favicon():
    """Serve favicon"""
    return send_file('image/logo.png')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/15%20emotion%20illustrations/<filename>')
def emotion_illustrations(filename):
    """Serve emotion illustration files"""
    return send_from_directory('15 emotion illustrations', filename)

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return send_from_directory('.', filename)

@app.route('/save-palette', methods=['POST'])
def save_palette():
    """API endpoint to save palette"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No image file provided'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type'}), 400
        
        # Get colours from form data
        colours = []
        if 'colours' in request.form:
            try:
                colours = json.loads(request.form['colours'])
            except json.JSONDecodeError:
                colours = []
        
        # Generate unique filename
        filename = generate_unique_filename()
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Save the file
        file.save(file_path)
        
        # Create metadata file
        metadata_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{Path(filename).stem}.json")
        metadata = {
            'filename': filename,
            'colours': colours,
            'timestamp': datetime.now().isoformat(),
            'size': os.path.getsize(file_path),
            'originalName': file.filename
        }
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Save to database if available
        if DB_ENABLED:
            try:
                session_id = request.headers.get('X-Session-ID', str(uuid.uuid4()))
                user_agent = request.headers.get('User-Agent')
                ip_address = request.environ.get('REMOTE_ADDR')
                
                # Create or get user
                db.create_or_get_user(session_id, user_agent, ip_address)
                
                # Save palette to database
                palette_id = db.save_palette(
                    filename=filename,
                    original_name=file.filename,
                    colors=colours,
                    file_size=os.path.getsize(file_path),
                    session_id=session_id,
                    metadata=metadata
                )
                
                logger.info(f"Palette saved to database with ID: {palette_id}")
                
            except Exception as e:
                logger.error(f"Failed to save palette to database: {e}")
        
        # Generate public URL
        base_url = f"{request.scheme}://{request.host}"
        image_url = f"{base_url}/uploads/{filename}"
        
        logger.info(f"Palette saved: {filename}")
        logger.info(f"Colours: {', '.join(colours)}")
        
        return jsonify({
            'success': True,
            'url': image_url,
            'filename': filename,
            'colours': colours,
            'metadata': metadata
        })
        
    except Exception as e:
        logger.error(f"Error saving palette: {e}")
        return jsonify({
            'error': 'Failed to save palette',
            'message': str(e)
        }), 500

@app.route('/palette/<filename>')
def get_palette_info(filename):
    """API endpoint to get palette info"""
    try:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        metadata_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{Path(filename).stem}.json")
        
        # Check if files exist
        if not os.path.exists(image_path) or not os.path.exists(metadata_path):
            return jsonify({'error': 'Palette not found'}), 404
        
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        base_url = f"{request.scheme}://{request.host}"
        
        return jsonify({
            **metadata,
            'url': f"{base_url}/uploads/{filename}",
            'exists': True
        })
        
    except Exception as e:
        logger.error(f"Error fetching palette info: {e}")
        return jsonify({
            'error': 'Failed to fetch palette info',
            'message': str(e)
        }), 500

@app.route('/recent-palettes')
def get_recent_palettes():
    """API endpoint to list recent palettes"""
    try:
        limit = int(request.args.get('limit', 20))
        
        # Get all JSON files in uploads directory
        json_files = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if f.endswith('.json')]
        
        palettes = []
        for file in json_files:
            try:
                with open(os.path.join(app.config['UPLOAD_FOLDER'], file), 'r') as f:
                    metadata = json.load(f)
                    base_url = f"{request.scheme}://{request.host}"
                    palettes.append({
                        **metadata,
                        'url': f"{base_url}/uploads/{metadata['filename']}"
                    })
            except:
                continue
        
        # Sort by timestamp (most recent first) and limit
        valid_palettes = sorted(
            palettes,
            key=lambda p: p.get('timestamp', ''),
            reverse=True
        )[:limit]
        
        return jsonify({
            'palettes': valid_palettes,
            'total': len(valid_palettes)
        })
        
    except Exception as e:
        logger.error(f"Error fetching recent palettes: {e}")
        return jsonify({
            'error': 'Failed to fetch recent palettes',
            'message': str(e)
        }), 500

@app.route('/session-palette/<session_id>')
def get_session_palette(session_id):
    """API endpoint to get the latest palette data for a specific session"""
    try:
        logger.info(f"📦 Getting palette data for session: {session_id}")
        
        # Check if session exists in memory
        if session_id not in session_storage:
            logger.warning(f"⚠️ Session not found in memory: {session_id}")
            return jsonify({'error': 'Session not found'}), 404
        
        session_data = session_storage[session_id]
        captured_palette = session_data.get('captured_palette')
        
        if not captured_palette:
            logger.warning(f"⚠️ No captured palette found for session: {session_id}")
            return jsonify({'error': 'No palette data found for this session'}), 404
        
        filename = captured_palette['filename']
        logger.info(f"🎨 Found palette file: {filename}")
        
        # Get the corresponding JSON metadata file
        metadata_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{Path(filename).stem}.json")
        
        if not os.path.exists(metadata_path):
            logger.warning(f"⚠️ Metadata file not found: {metadata_path}")
            # Run analysis if metadata doesn't exist
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.exists(image_path):
                logger.info(f"🔄 Re-running analysis for {filename}")
                result = run_python_script(None, image_path)
                
        # Return the fresh analysis result
        base_url = f"{request.scheme}://{request.host}"
        return jsonify({
                    'success': True,
                    'filename': filename,
                    'colourData': result.get('colourData', {}),
                    'rawColors': result.get('rawColors', []),
                    'emotionPrediction': result.get('emotionPrediction', {}),
                    'detailedRecommendations': result.get('detailedRecommendations', []),
            'capturedImageUrl': f"{base_url}/uploads/{filename}",
                    'sessionId': session_id,
                    'timestamp': captured_palette.get('timestamp'),
                    'gifName': captured_palette.get('gifName')
                })
            else:
                return jsonify({'error': 'Palette image file not found'}), 404
        
        # Read existing metadata
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        base_url = f"{request.scheme}://{request.host}"
        
        # Return the complete palette data
        response_data = {
            'success': True,
            'filename': filename,
            'colourData': metadata.get('colourData', {}),
            'rawColors': metadata.get('rawColors', []),
            'emotionPrediction': metadata.get('emotionPrediction', {}),
            'detailedRecommendations': metadata.get('detailedRecommendations', []),
            'capturedImageUrl': f"{base_url}/uploads/{filename}",
            'sessionId': session_id,
            'timestamp': captured_palette.get('timestamp'),
            'gifName': captured_palette.get('gifName')
        }
        
        logger.info(f"✅ Successfully retrieved palette data for session: {session_id}")
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"❌ Error fetching session palette: {e}")
        return jsonify({
            'error': 'Failed to fetch session palette',
            'message': str(e)
        }), 500

@app.route('/get-recommendations', methods=['POST'])
def get_recommendations():
    """API endpoint to get painting recommendations"""
    try:
        data = request.get_json()
        if not data or 'filename' not in data:
            return jsonify({'error': 'Filename is required'}), 400
        
        filename = data['filename']
        logger.info(f"Getting recommendations for: {filename}")
        
        # Construct the full image path from uploads directory
        full_image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Check if the image file exists
        if not os.path.exists(full_image_path):
            return jsonify({'error': 'Image file not found'}), 404
        
        logger.info('Running Python recommendation script...')
        
        # Run the Python script
        result = run_python_script(None, full_image_path)
        
        # Use raw colors from Python output if available, otherwise fall back to JSON file
        raw_colors = result.get('rawColors', [])
        
        # If no raw colors from Python output, try reading from JSON file as fallback
        if not raw_colors:
            try:
                json_filename = filename.replace('.png', '.json')
                json_file_path = os.path.join(app.config['UPLOAD_FOLDER'], json_filename)
                logger.info(f'No raw colors from Python, reading from JSON: {json_file_path}')
                
                if os.path.exists(json_file_path):
                    with open(json_file_path, 'r') as f:
                        json_data = json.load(f)
                    if 'colours' in json_data and isinstance(json_data['colours'], list):
                        # Convert hex colors to raw color format with equal percentages
                        percentage = 1 / len(json_data['colours'])
                        raw_colors = [
                            {'hex': hex_color, 'percentage': percentage}
                            for hex_color in json_data['colours']
                        ]
                        logger.info(f'Found fallback hex colors: {raw_colors}')
                else:
                    logger.warning(f'JSON file not found: {json_file_path}')
            except Exception as e:
                logger.error(f'Error reading fallback raw colors: {e}')
        else:
            logger.info(f'Using raw RGB colors from Python output: {raw_colors}')

        logger.info(f"Found {len(result['urls'])} recommendations")
        logger.info(f"Colour data: {result['colourData']}")
        logger.info(f"Final raw colors for frontend: {raw_colors}")
        
        return jsonify({
            'success': True,
            'recommendations': result['urls'],
            'colourData': result['colourData'],
            'rawColors': raw_colors,
            'detailedRecommendations': result['detailedRecommendations'],
            'emotionPrediction': result['emotionPrediction'],
            'total': len(result['urls'])
        })
        
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        return jsonify({
            'error': 'Failed to get recommendations',
            'message': str(e)
        }), 500

@app.route('/predict-emotion', methods=['POST'])
def predict_emotion():
    """API endpoint for emotion prediction service (called after Capture button)"""
    try:
        data = request.get_json()
        if not data or 'filename' not in data:
            return jsonify({'error': 'Filename is required'}), 400
        
        filename = data['filename']
        logger.info(f"Predicting emotion for: {filename}")
        
        # Construct the full image path from uploads directory
        full_image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Check if the image file exists
        if not os.path.exists(full_image_path):
            return jsonify({'error': 'Image file not found'}), 404
        
        logger.info('Running emotion prediction service...')
        
        # Run the emotion prediction service
        emotion_result = run_emotion_prediction_service(full_image_path)
        
        logger.info(f"Emotion prediction completed: {emotion_result['emotionPrediction']['emotion']}")
        
        return jsonify({
            'success': True,
            'emotionPrediction': emotion_result['emotionPrediction'],
            'colourData': emotion_result['colourData'],
            'rawColors': emotion_result['rawColorsForFrontend'],
            'rawColorsForRecommendation': emotion_result['rawColors']  # This will be used by recommendation service
        })
        
    except Exception as e:
        logger.error(f"Error predicting emotion: {e}")
        return jsonify({
            'error': 'Failed to predict emotion',
            'message': str(e)
        }), 500

@app.route('/get-recommendations-from-colors', methods=['POST'])
def get_recommendations_from_colors():
    """API endpoint for recommendation service (called after Continue button)"""
    try:
        data = request.get_json()
        if not data or 'rawColors' not in data:
            return jsonify({'error': 'Raw colors data is required'}), 400
        
        raw_colors = data['rawColors']
        # Ensure the colors are enriched to the format expected by the recommendation script
        raw_colors = ensure_enriched_raw_colors(raw_colors)
        logger.info(f"Getting recommendations from {len(raw_colors)} raw colors")
        
        # Validate raw colors format
        if not isinstance(raw_colors, list) or len(raw_colors) != 5:
            return jsonify({'error': 'Expected 5 raw colors'}), 400
        
        logger.info('Running recommendation service...')
        
        # Convert raw colors to JSON string for the recommendation service
        raw_colors_json = json.dumps(raw_colors)
        
        # Run the recommendation service
        recommendation_result = run_recommendation_service(raw_colors_json)
        
        logger.info(f"Found {len(recommendation_result['urls'])} recommendations")
        
        return jsonify({
            'success': True,
            'recommendations': recommendation_result['urls'],
            'detailedRecommendations': recommendation_result['detailedRecommendations'],
            'total': len(recommendation_result['urls'])
        })
        
    except Exception as e:
        logger.error(f"Error getting recommendations from colors: {e}")
        return jsonify({
            'error': 'Failed to get recommendations',
            'message': str(e)
        }), 500

@app.route('/save-selection', methods=['POST'])
def save_selection():
    """API endpoint to save user's selected paintings"""
    try:
        data = request.get_json()
        
        if not data or 'selectedPaintings' not in data:
            return jsonify({'error': 'Selected paintings are required'}), 400
        
        selected_paintings = data['selectedPaintings']
        character = data.get('character', '')
        nickname = data.get('nickname', '')
        emotion = data.get('emotion', '')
        probability = data.get('probability', 0)
        session_id = get_or_create_session(data)
        
        if not isinstance(selected_paintings, list) or len(selected_paintings) != 3:
            return jsonify({'error': 'Exactly 3 selected paintings are required'}), 400
        
        # Update session storage
        if session_id in session_storage:
            session_storage[session_id]['selected_paintings'] = selected_paintings
            session_storage[session_id]['character'] = character
            session_storage[session_id]['nickname'] = nickname
            session_storage[session_id]['emotion'] = emotion
            session_storage[session_id]['probability'] = probability
        
        logger.info(f"🖼️ PAINTING SELECTION:")
        logger.info(f"   Session: {session_id}")
        logger.info(f"   Character: {character}")
        logger.info(f"   Nickname: {nickname}")
        logger.info(f"   Emotion: {emotion}")
        logger.info(f"   Probability: {probability}")
        logger.info("   Selected paintings:")
        for i, painting in enumerate(selected_paintings):
            logger.info(f"     {i + 1}. {painting.get('title', 'Unknown')} by {painting.get('artist', 'Unknown')}")
        
        # Save to database if available
        if DB_ENABLED:
            try:
                painting_urls = [p.get('url', '') for p in selected_paintings]
                db.save_paintings_style(
                    session_id=session_id,
                    painting_urls=painting_urls,
                    story_character=character,
                    nickname=nickname
                )
                logger.info(f"✅ Painting selection saved to database for session: {session_id}")
            except Exception as e:
                logger.error(f"❌ Failed to save painting selection to database: {e}")
        
        return jsonify({
            'success': True,
            'sessionId': session_id,
            'message': 'Selection saved successfully',
            'selectedPaintings': selected_paintings,
            'character': character,
            'nickname': nickname,
            'emotion': emotion,
            'probability': probability
        })
        
    except Exception as e:
        logger.error(f"Error saving selection: {e}")
        return jsonify({
            'error': 'Failed to save selection',
            'message': str(e)
        }), 500

@app.route('/save-emotion', methods=['POST'])
def save_emotion():
    """API endpoint to save user's emotion selection from Step 1"""
    try:
        data = request.get_json()
        
        if not data or 'emotion' not in data:
            return jsonify({'error': 'Emotion is required'}), 400
        
        emotion = data['emotion']
        probability = data.get('probability')
        session_id = get_or_create_session(data)
        
        # Update session storage
        if session_id in session_storage:
            session_storage[session_id]['selected_emotion'] = {
                'emotion': emotion,
                'probability': probability,
                'timestamp': datetime.now().isoformat()
            }
        
        logger.info('🎭 EMOTION SELECTION:')
        logger.info(f'   User selected emotion: {emotion}')
        logger.info(f'   Probability: {probability}%')
        logger.info(f'   Session ID: {session_id}')
        
        # Save to database if available
        if DB_ENABLED:
            try:
                db.save_emotion_selection(
                    session_id=session_id,
                    selected_emotion=emotion,
                    probability=probability
                )
                logger.info(f"✅ Emotion saved to database for session: {session_id}")
            except Exception as e:
                logger.error(f"❌ Failed to save emotion to database: {e}")
        
        return jsonify({
            'success': True,
            'sessionId': session_id,
            'message': 'Emotion selection saved successfully',
            'selectedEmotion': {
                'emotion': emotion,
                'probability': probability
            }
        })
        
    except Exception as e:
        logger.error(f"Error saving emotion selection: {e}")
        return jsonify({
            'error': 'Failed to save emotion selection',
            'message': str(e)
        }), 500

@app.route('/selection-history')
def get_selection_history():
    """API endpoint to get user's selection history"""
    try:
        limit = int(request.args.get('limit', 10))
        
        # Get all selection files
        selection_files = [
            f for f in os.listdir(app.config['UPLOAD_FOLDER'])
            if f.startswith('selection-') and f.endswith('.json')
        ]
        
        selections = []
        for file in selection_files:
            try:
                with open(os.path.join(app.config['UPLOAD_FOLDER'], file), 'r') as f:
                    selection_data = json.load(f)
                    selections.append({
                        **selection_data,
                        'filename': file
                    })
            except:
                continue
        
        # Sort by timestamp (most recent first) and limit
        valid_selections = sorted(
            selections,
            key=lambda s: s.get('selectionTimestamp', ''),
            reverse=True
        )[:limit]
        
        return jsonify({
            'selections': valid_selections,
            'total': len(valid_selections)
        })
        
    except Exception as e:
        logger.error(f"Error fetching selection history: {e}")
        return jsonify({
            'error': 'Failed to fetch selection history',
            'message': str(e)
        }), 500

@app.route('/generate-story', methods=['POST'])
def generate_story():
    """API endpoint to generate story"""
    try:
        logger.info("🔮 Starting generate_story endpoint")
        data = request.get_json()
        logger.info(f"🔮 Received data: {data is not None}")
        
        session_id = get_or_create_session(data)
        logger.info(f"🔮 Session ID: {session_id}")
        
        # Extract data from the new format
        paintings = data.get('paintings') if data else None
        character = data.get('character') if data else None  
        nickname = data.get('nickname') if data else None
        emotion = data.get('emotion') if data else None
        probability = data.get('probability') if data else None
        timestamp = data.get('timestamp') if data else None
        
        logger.info(f"🔮 Received data: paintings={len(paintings) if paintings else 'None'}, character={character}, nickname={nickname}")
        logger.info(f"🔮 Emotion data: {emotion} ({probability}%), timestamp={timestamp}")
        
        # Fallback to session data if not provided in request
        session_data = session_storage.get(session_id, {})
        
        if not paintings:
            paintings = session_data.get('selected_paintings', [])
            logger.info(f"🔮 Using paintings from session: {len(paintings)}")
        
        if not character:
            character = session_data.get('character', '')
            
        if not nickname:
            nickname = session_data.get('nickname', '')
            
        if not emotion:
            # Check for emotion data stored by save-emotion endpoint
            selected_emotion_data = session_data.get('selected_emotion', {})
            if selected_emotion_data and isinstance(selected_emotion_data, dict):
                emotion = selected_emotion_data.get('emotion', '')
            else:
                emotion = session_data.get('emotion', '')
            
        if not probability:
            # Check for probability data stored by save-emotion endpoint
            selected_emotion_data = session_data.get('selected_emotion', {})
            if selected_emotion_data and isinstance(selected_emotion_data, dict):
                probability = selected_emotion_data.get('probability', 0)
            else:
                probability = session_data.get('probability', 0)
        
        logger.info(f"🔮 Final values - paintings: {len(paintings) if paintings else 'None'}, character: {character}, nickname: {nickname}")
        logger.info(f"🔮 Final emotion values - emotion: {emotion}, probability: {probability}")
        
        # Debug session storage for emotion data
        selected_emotion_data = session_data.get('selected_emotion', {})
        logger.info(f"🔮 Session emotion debug - selected_emotion_data: {selected_emotion_data}")
        logger.info(f"🔮 Session emotion debug - session keys: {list(session_data.keys())}")
        logger.info(f"🔮 Request emotion debug - request emotion: {data.get('emotion') if data else 'No data'}")
        logger.info(f"🔮 Request emotion debug - request probability: {data.get('probability') if data else 'No data'}")
        
        if not paintings or len(paintings) != 3:
            return jsonify({'error': 'Exactly 3 paintings are required'}), 400
        
        # Set default narrative style (could be made configurable)
        narrative_style = data.get('narrative_style', 'adventure')
        
        logger.info(f"📚 STORY GENERATION:")
        logger.info(f"   Session: {session_id}")
        logger.info(f"   User: {nickname}")
        logger.info(f"   Character: {character}")
        logger.info(f"   Emotion: {emotion} ({probability}%)")
        logger.info(f"   Paintings: {[p.get('title', 'Unknown') for p in paintings]}")
        
        # Download images for each painting (supports Google Arts & Culture and proxied URLs)
        paintings_with_images = []
        for i, painting in enumerate(paintings):
            image_filename = f"story_image_{int(datetime.now().timestamp() * 1000)}_{i}.jpg"
            
            try:
                logger.info(f"Downloading image {i + 1}: {painting['url']}")
                image_path = download_image(painting['url'], image_filename)
                
                # Verify the downloaded file exists
                if not os.path.exists(image_path):
                    raise Exception(f"Downloaded file not found: {image_path}")
                
                paintings_with_images.append({
                    **{k: v for k, v in painting.items() if k != 'year'},
                    'imagePath': image_path,
                    'imageFilename': image_filename
                })
            except Exception as e:
                logger.error(f"Failed to download image {i + 1}: {e}")
                return jsonify({
                    'error': 'Failed to download painting images',
                    'message': str(e)
                }), 500
        
        # Prepare input for story API service
        input_data = {
            'paintings': paintings_with_images,
            'character': character,
            'nickname': nickname,
            'emotion': emotion,
            'emotion_probability': probability,
            'timestamp': timestamp
        }
        
        logger.info(f"Generating {narrative_style} story with {len(input_data['paintings'])} paintings")
        
        # Call the story API service instead of running script directly
        story_api_url = os.environ.get('STORY_API_URL', 'http://story-api:5002')
        logger.info(f"🔮 Calling story API: {story_api_url}/generate")
        logger.info(f"🔮 Input data keys: {list(input_data.keys())}")
        logger.info(f"🔮 Number of paintings: {len(input_data.get('paintings', []))}")
        
        try:
            logger.info(f"🔮 Making POST request to story API...")
            story_response = requests.post(
                f"{story_api_url}/generate",
                json=input_data,
                timeout=60  # 1 minute timeout for story generation
            )
            logger.info(f"🔮 Story API response status: {story_response.status_code}")
            logger.info(f"🔮 Story API response headers: {dict(story_response.headers)}")
            
            story_response.raise_for_status()
            result = story_response.json()
            
            logger.info(f"🔮 Story API response type: {type(result)}")
            logger.info(f"🔮 Story API response keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Failed to call story API: {e}")
            logger.error(f"❌ Response content: {getattr(e.response, 'content', 'No response content')}")
            result = {
                'success': False,
                'error': f'Story API service unavailable: {str(e)}'
            }
        except Exception as e:
            logger.error(f"❌ Unexpected error calling story API: {e}")
            result = {
                'success': False,
                'error': f'Unexpected error: {str(e)}'
            }
        
        # Store story in session
        if result.get('success'):
            session_storage[session_id]['story_data'] = result
        
        # Clean up downloaded images
        for painting in paintings_with_images:
            try:
                os.unlink(painting['imagePath'])
                logger.info(f"Cleaned up image: {painting['imageFilename']}")
            except Exception as e:
                logger.error(f"Failed to clean up image {painting['imageFilename']}: {e}")
        
        if result.get('success'):
            logger.info(f"✅ Story generated successfully ({result.get('word_count')} words)")
            return jsonify({
                **result,
                'sessionId': session_id
            })
        else:
            logger.error(f"❌ Story generation failed: {result.get('error')}")
            return jsonify({
                'error': 'Failed to generate story',
                'message': result.get('error')
            }), 500
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"Error generating story: {e}")
        logger.error(f"Full traceback: {error_trace}")
        
        # Clean up downloaded images in case of error
        if 'paintings_with_images' in locals():
            for painting in paintings_with_images:
                try:
                    os.unlink(painting['imagePath'])
                    logger.info(f"Cleaned up image after error: {painting['imageFilename']}")
                except Exception as cleanup_error:
                    logger.error(f"Failed to clean up image {painting['imageFilename']}: {cleanup_error}")
        
        return jsonify({
            'error': 'Failed to generate story',
            'message': str(e)
        }), 500

@app.route('/submit-feedback', methods=['POST'])
def submit_feedback():
    """API endpoint to submit user feedback"""
    try:
        data = request.get_json()
        session_id = get_or_create_session(data)
        
        # Extract answers data (q1-q13 as integers 1-5, q14-q15 as text)
        answers = data.get('answers', {})
        
        logger.info(f"📝 FEEDBACK SUBMISSION:")
        logger.info(f"   Session: {session_id}")
        logger.info(f"   Q1-Q13 ratings: {[answers.get(f'q{i}') for i in range(1, 14)]}")
        logger.info(f"   Q14 (liked most): {answers.get('q14', '')[:50]}...")
        logger.info(f"   Q15 (improvements): {answers.get('q15', '')[:50]}...")
        
        # Save to database if available
        if DB_ENABLED:
            try:
                # Prepare feedback form data
                feedback_form_data = {
                    'q1': answers.get('q1'),
                    'q2': answers.get('q2'),
                    'q3': answers.get('q3'),
                    'q4': answers.get('q4'),
                    'q5': answers.get('q5'),
                    'q6': answers.get('q6'),
                    'q7': answers.get('q7'),
                    'q8': answers.get('q8'),
                    'q9': answers.get('q9'),
                    'q10': answers.get('q10'),
                    'q11': answers.get('q11'),
                    'q12': answers.get('q12'),
                    'q13': answers.get('q13'),
                    'q14': answers.get('q14') if answers.get('q14') else None,
                    'q15': answers.get('q15') if answers.get('q15') else None
                }
                
                db.save_feedback_form(
                    session_id=session_id,
                    feedback_data=feedback_form_data
                )
                logger.info(f"✅ Feedback saved to database for session: {session_id}")
            except Exception as e:
                logger.error(f"❌ Failed to save feedback to database: {e}")
        
        return jsonify({
            'success': True,
            'sessionId': session_id,
            'message': 'Feedback submitted successfully'
        })
        
    except Exception as e:
        logger.error(f"Error submitting feedback: {e}")
        return jsonify({
            'error': 'Failed to submit feedback',
            'message': str(e)
        }), 500

@app.route('/proxy-image')
def proxy_image():
    """Proxy external painting images to avoid CORS/ORB issues"""
    try:
        image_url = request.args.get('url')
        if not image_url:
            return jsonify({'error': 'URL parameter required'}), 400
        
        # Validate URL
        if not (image_url.startswith('http://') or image_url.startswith('https://')):
            return jsonify({'error': 'Invalid URL'}), 400
        
        logger.info(f"Proxying image: {image_url}")
        
        # Enhanced headers for better compatibility
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'image',
            'Sec-Fetch-Mode': 'no-cors',
            'Sec-Fetch-Site': 'cross-site'
        }
        
        # Special handling for Google Arts & Culture URLs
        if 'googleusercontent.com' in image_url or 'artsandculture.google.com' in image_url:
            # Add specific parameters for Google images
            if '=' not in image_url and 'googleusercontent.com' in image_url:
                image_url += '=s800'  # Request reasonable resolution
            headers['Referer'] = 'https://artsandculture.google.com/'
            # Remove some headers that might cause issues with Google
            headers.pop('DNT', None)
            headers.pop('Sec-Fetch-Dest', None)
            headers.pop('Sec-Fetch-Mode', None)
            headers.pop('Sec-Fetch-Site', None)
        
        response = requests.get(image_url, headers=headers, timeout=15, stream=True, allow_redirects=True)
        
        # Check if we got a valid response
        if response.status_code != 200:
            logger.warning(f"Non-200 response for {image_url}: {response.status_code}")
            # Try a fallback approach with minimal headers
            simple_headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; ImageProxy/1.0)'
            }
            response = requests.get(image_url, headers=simple_headers, timeout=15, stream=True, allow_redirects=True)
        
        response.raise_for_status()
        
        # Get content type and validate it's an image
        content_type = response.headers.get('content-type', 'image/jpeg')
        if not content_type.startswith('image/'):
            logger.warning(f"Non-image content type for {image_url}: {content_type}")
            content_type = 'image/jpeg'  # Default fallback
        
        logger.info(f"Successfully proxied image: {image_url} ({content_type})")
        
        # Return the image with proper headers
        return Response(
            response.content,
            content_type=content_type,
            headers={
                'Cache-Control': 'public, max-age=3600',  # Cache for 1 hour
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET',
                'Access-Control-Allow-Headers': 'Origin, X-Requested-With, Content-Type, Accept'
            }
        )
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error proxying image {image_url}: {e}")
        # Return a simple placeholder image instead of error
        return generate_placeholder_image()
    except Exception as e:
        logger.error(f"Unexpected error proxying image: {e}")
        return generate_placeholder_image()

def generate_placeholder_image():
    """Generate a simple placeholder image for failed image loads"""
    try:
        # Create a simple SVG placeholder
        svg_content = '''<svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
            <rect width="400" height="300" fill="#2a2a2a"/>
            <rect x="10" y="10" width="380" height="280" fill="none" stroke="#666" stroke-width="2" stroke-dasharray="5,5"/>
            <text x="200" y="140" text-anchor="middle" fill="#999" font-family="Arial, sans-serif" font-size="16">
                Painting Image
            </text>
            <text x="200" y="160" text-anchor="middle" fill="#666" font-family="Arial, sans-serif" font-size="12">
                Loading...
            </text>
        </svg>'''
        
        return Response(
            svg_content,
            content_type='image/svg+xml',
            headers={
                'Cache-Control': 'public, max-age=300',  # Cache for 5 minutes
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET',
                'Access-Control-Allow-Headers': 'Origin, X-Requested-With, Content-Type, Accept'
            }
        )
    except Exception as e:
        logger.error(f"Failed to generate placeholder image: {e}")
        return jsonify({'error': 'Failed to generate placeholder'}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    health_data = {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'components': {
            'server': 'healthy',
            'filesystem': 'healthy'
        }
    }
    
    # Check database if enabled (but don't fail health check if DB is temporarily down)
    if DB_ENABLED:
        try:
            if db.health_check():
                health_data['components']['database'] = 'healthy'
            else:
                health_data['components']['database'] = 'unhealthy'
                health_data['status'] = 'degraded'  # degraded but still return 200
        except Exception as e:
            health_data['components']['database'] = f'error: {str(e)}'
            health_data['status'] = 'degraded'  # degraded but still return 200
    else:
        health_data['components']['database'] = 'disabled'
    
    # Check uploads directory (this is critical for app function)
    if not os.path.exists(UPLOAD_FOLDER):
        health_data['components']['filesystem'] = 'uploads directory missing'
        health_data['status'] = 'unhealthy'
        return jsonify(health_data), 503  # Only return 503 for critical failures
    
    # Always return 200 unless there's a critical filesystem issue
    # Database being down shouldn't restart the container
    return jsonify(health_data), 200

# Error handling

@app.errorhandler(413)
def file_too_large(e):
    return jsonify({'error': 'File too large'}), 413

@app.errorhandler(400)
def bad_request(e):
    return jsonify({'error': 'Bad request'}), 400

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    logger.error(f"Internal server error: {e}")
    return jsonify({
        'error': 'Internal server error',
        'message': str(e) if app.debug else 'Something went wrong'
    }), 500

# Graceful shutdown handling
def signal_handler(sig, frame):
    logger.info(f"Signal {sig} received, shutting down gracefully")
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

if __name__ == '__main__':
    logger.info(f"🚀 Gradient Palette Server running on http://localhost:{PORT}")
    logger.info(f"📁 Uploads directory: {UPLOAD_FOLDER}")
    logger.info(f"🎨 Ready to create beautiful palettes!")
    
    app.run(
        host='0.0.0.0',
        port=PORT,
        debug=os.environ.get('FLASK_ENV') == 'development'
    ) 
