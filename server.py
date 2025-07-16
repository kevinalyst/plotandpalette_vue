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
UPLOAD_FOLDER = 'uploads'
PUBLIC_FOLDER = 'public'
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Ensure directories exist
def ensure_directory_exists(directory: str):
    Path(directory).mkdir(parents=True, exist_ok=True)

ensure_directory_exists(UPLOAD_FOLDER)
ensure_directory_exists(PUBLIC_FOLDER)

# Configure Flask upload settings
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

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
        response = requests.get(url, timeout=30, stream=True)
        response.raise_for_status()
        
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        with open(file_path, 'wb') as f:
            shutil.copyfileobj(response.raw, f)
        
        return file_path
    except Exception as e:
        logger.error(f"Failed to download image {url}: {e}")
        raise

def run_python_script(script_path: str, image_path: str = None) -> Dict[str, Any]:
    """Run Python recommendation script and parse output"""
    try:
        # Use the embedded Python script
        embedded_script_path = os.path.join(os.getcwd(), 'recommendation_service_embedded.py')
        
        # Use virtual environment Python if available, otherwise fall back to system Python
        venv_python = os.path.join(os.getcwd(), 'venv', 'bin', 'python3')
        if os.path.exists(venv_python):
            python_executable = venv_python
        else:
            python_executable = 'python3'
        
        args = [python_executable, embedded_script_path]
        
        if image_path:
            args.append(image_path)
        
        logger.info(f"Running embedded recommendation script: {' '.join(args)}")
        
        result = subprocess.run(
            args,
            cwd=os.getcwd(),
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode != 0:
            logger.error(f"Embedded recommendation script error: {result.stderr}")
            raise Exception(f"Embedded recommendation script failed with code {result.returncode}: {result.stderr}")
        
        logger.info("Embedded recommendation script completed successfully")
        
        # Parse the output to extract URLs, colour data, and detailed recommendations
        parsed_result = parse_recommendation_output(result.stdout)
        return parsed_result
        
    except Exception as e:
        logger.error(f"Error running Python recommendation script: {e}")
        raise

def parse_recommendation_output(output: str) -> Dict[str, Any]:
    """Parse Python script output and extract URLs, colour data, and detailed recommendations"""
    urls = []
    lines = output.split('\n')
    
    in_recommendation_section = False
    colour_data = {}
    raw_color_data = []
    detailed_recommendations = []
    emotion_prediction = None
    
    # Parse raw extracted colors and mapped colour percentages
    for line in lines:
        # Parse raw RGB colors from the new format: "  Raw Color 1: RGB(255, 165, 0) - 42.36%"
        import re
        raw_color_match = re.search(r'\s*Raw Color \d+: RGB\((\d+), (\d+), (\d+)\) - ([\d.]+)%', line)
        if raw_color_match:
            r = int(raw_color_match.group(1))
            g = int(raw_color_match.group(2))
            b = int(raw_color_match.group(3))
            percentage = float(raw_color_match.group(4)) / 100  # Convert percentage to decimal
            raw_color_data.append({'r': r, 'g': g, 'b': b, 'percentage': percentage})
        
        # Also parse old format for backwards compatibility
        old_raw_color_match = re.search(r'Analyzing extracted color: RGB\(.*?(\d+).*?(\d+).*?(\d+)\)', line)
        if old_raw_color_match and len(raw_color_data) == 0:  # Only use if new format not found
            r = int(old_raw_color_match.group(1))
            g = int(old_raw_color_match.group(2))
            b = int(old_raw_color_match.group(3))
            raw_color_data.append({'r': r, 'g': g, 'b': b})
        
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

def run_python_story_script(script_path: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Run Python story generation script"""
    try:
        input_json = json.dumps(input_data)
        
        # Use virtual environment Python if available, otherwise fall back to system Python
        venv_python = os.path.join(os.getcwd(), 'venv', 'bin', 'python3')
        if os.path.exists(venv_python):
            python_executable = venv_python
        else:
            python_executable = 'python3'
        
        result = subprocess.run(
            [python_executable, script_path, input_json],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode != 0:
            logger.error(f"Python story script error: {result.stderr}")
            return {
                'success': False,
                'error': result.stderr or 'Story generation failed'
            }
        
        try:
            # Log the raw output for debugging
            logger.info(f"Raw Python output length: {len(result.stdout)}")
            logger.info(f"Raw Python stderr: {result.stderr}")
            
            # Try to parse the entire stdout as JSON first
            try:
                parsed_result = json.loads(result.stdout.strip())
                logger.info("Successfully parsed entire stdout as JSON")
                return parsed_result
            except json.JSONDecodeError:
                logger.info("Direct JSON parse failed, trying line-by-line extraction...")
            
            # Extract JSON from stdout (may contain logging info)
            lines = result.stdout.strip().split('\n')
            json_start_index = -1
            brace_count = 0
            json_end_index = -1
            
            # Find the first line that contains '{'
            for i, line in enumerate(lines):
                if '{' in line:
                    json_start_index = i
                    break
            
            if json_start_index == -1:
                raise Exception('No JSON start found in output')
            
            # Find the matching closing brace by counting braces
            for i in range(json_start_index, len(lines)):
                line = lines[i]
                for char in line:
                    if char == '{':
                        brace_count += 1
                    if char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            json_end_index = i
                            break
                if json_end_index != -1:
                    break
            
            if json_end_index == -1:
                raise Exception('No JSON end found in output')
            
            # Extract and parse JSON
            json_lines = lines[json_start_index:json_end_index + 1]
            json_str = '\n'.join(json_lines)
            
            logger.info(f"Extracted JSON length: {len(json_str)}")
            logger.info(f"JSON preview: {json_str[:100]}...")
            
            parsed_result = json.loads(json_str)
            return parsed_result
            
        except Exception as e:
            logger.error(f"Error parsing story result: {e}")
            logger.error(f"Raw stdout (first 500 chars): {result.stdout[:500]}")
            logger.error(f"Raw stderr: {result.stderr}")
            return {
                'success': False,
                'error': 'Failed to parse story generation result'
            }
            
    except Exception as e:
        logger.error(f"Failed to start Python story script: {e}")
        return {
            'success': False,
            'error': 'Failed to start story generator'
        }

# Routes

@app.route('/api/health')
def health_check():
    """A simple health check endpoint."""
    return jsonify({'status': 'ok', 'message': 'Backend is healthy'}), 200

@app.route('/api/status')
def status_check():
    """A simple status endpoint."""
    return jsonify({'status': 'running'}), 200

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

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return send_from_directory('.', filename)

@app.route('/api/save-palette', methods=['POST'])
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

@app.route('/api/palette/<filename>')
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

@app.route('/api/recent-palettes')
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

@app.route('/api/get-recommendations', methods=['POST'])
def get_recommendations():
    """API endpoint to get painting recommendations"""
    try:
        data = request.get_json()
        if not data or 'filename' not in data:
            return jsonify({'error': 'Filename is required'}), 400
        
        filename = data['filename']
        logger.info(f"Getting recommendations for: {filename}")
        
        # Construct the full image path
        image_path = f"uploads/{filename}"
        full_image_path = os.path.join(os.getcwd(), image_path)
        
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

@app.route('/api/save-selection', methods=['POST'])
def save_selection():
    """API endpoint to save user's selected paintings"""
    try:
        data = request.get_json()
        
        if not data or 'selectedPaintings' not in data or 'originalFilename' not in data:
            return jsonify({'error': 'Selected paintings and original filename are required'}), 400
        
        selected_paintings = data['selectedPaintings']
        original_filename = data['originalFilename']
        session_id = data.get('sessionId', str(uuid.uuid4()))
        
        if not isinstance(selected_paintings, list) or len(selected_paintings) != 3:
            return jsonify({'error': 'Exactly 3 selected paintings are required'}), 400
        
        logger.info(f"Saving selection for {original_filename}: {selected_paintings}")
        
        # Create selection metadata
        selection_data = {
            'originalFilename': original_filename,
            'sessionId': session_id,
            'selectedPaintings': [
                {
                    'url': painting['url'],
                    'index': painting['index'],
                    'slot': painting['slot'],
                    'timestamp': datetime.now().isoformat()
                }
                for painting in selected_paintings
            ],
            'totalRecommendations': 10,
            'selectionTimestamp': datetime.now().isoformat(),
            'userAgent': request.headers.get('User-Agent', 'Unknown')
        }
        
        # Save selection to file
        selection_filename = f"selection-{int(datetime.now().timestamp() * 1000)}-{str(uuid.uuid4())[:8]}.json"
        selection_path = os.path.join(app.config['UPLOAD_FOLDER'], selection_filename)
        
        with open(selection_path, 'w') as f:
            json.dump(selection_data, f, indent=2)
        
        logger.info(f"Selection saved to: {selection_filename}")
        logger.info("Selected painting URLs:")
        for i, painting in enumerate(selected_paintings):
            logger.info(f"  {i + 1}. Slot {painting['slot'] + 1}: {painting['url']}")
        
        return jsonify({
            'success': True,
            'selectionId': selection_data['sessionId'],
            'selectionFilename': selection_filename,
            'message': 'Selection saved successfully',
            'selectedPaintings': selection_data['selectedPaintings']
        })
        
    except Exception as e:
        logger.error(f"Error saving selection: {e}")
        return jsonify({
            'error': 'Failed to save selection',
            'message': str(e)
        }), 500

@app.route('/api/save-emotion', methods=['POST'])
def save_emotion():
    """API endpoint to save user's emotion selection from Step 1"""
    try:
        data = request.get_json()
        
        if not data or 'emotion' not in data or 'filename' not in data:
            return jsonify({'error': 'Emotion and filename are required'}), 400
        
        emotion = data['emotion']
        probability = data.get('probability')
        filename = data['filename']
        session_id = data.get('sessionId', str(uuid.uuid4()))
        
        logger.info('🎭 EMOTION SELECTION:')
        logger.info(f'   User selected emotion: {emotion}')
        logger.info(f'   Probability: {probability}%')
        logger.info(f'   For palette: {filename}')
        logger.info(f'   Session ID: {session_id}')
        
        # Create emotion selection metadata
        emotion_data = {
            'emotion': emotion,
            'probability': probability,
            'filename': filename,
            'sessionId': session_id,
            'timestamp': datetime.now().isoformat(),
            'userAgent': request.headers.get('User-Agent', 'Unknown')
        }
        
        # Save emotion selection to file
        emotion_filename = f"emotion-{int(datetime.now().timestamp() * 1000)}-{str(uuid.uuid4())[:8]}.json"
        emotion_path = os.path.join(app.config['UPLOAD_FOLDER'], emotion_filename)
        
        with open(emotion_path, 'w') as f:
            json.dump(emotion_data, f, indent=2)
        
        logger.info(f'   Emotion selection saved to: {emotion_filename}')
        
        return jsonify({
            'success': True,
            'emotionId': emotion_data['sessionId'],
            'emotionFilename': emotion_filename,
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

@app.route('/api/selection-history')
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

@app.route('/api/generate-story', methods=['POST'])
def generate_story():
    """API endpoint to generate story"""
    try:
        data = request.get_json()
        
        if not data or 'paintings' not in data or 'narrative_style' not in data:
            return jsonify({'error': 'Paintings and narrative style are required'}), 400
        
        paintings = data['paintings']
        narrative_style = data['narrative_style']
        user_name = data.get('user_name', '')
        emotion = data.get('emotion')
        emotion_probability = data.get('emotion_probability')
        
        if not isinstance(paintings, list) or len(paintings) != 3:
            return jsonify({'error': 'Exactly 3 paintings are required'}), 400
        
        logger.info(f"Generating {narrative_style} story for paintings: {[p['title'] for p in paintings]}")
        if user_name:
            logger.info(f"User name: {user_name}")
        if emotion and emotion_probability is not None:
            logger.info(f"Emotion: {emotion} ({emotion_probability}%)")
        
        # Download images for each painting
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
                    **painting,
                    'imagePath': image_path,
                    'imageFilename': image_filename
                })
            except Exception as e:
                logger.error(f"Failed to download image {i + 1}: {e}")
                return jsonify({
                    'error': 'Failed to download painting images',
                    'message': str(e)
                }), 500
        
        # Prepare input for Python script with image paths and emotion data
        input_data = {
            'paintings': paintings_with_images,
            'narrative_style': narrative_style,
            'user_name': user_name,
            'emotion': emotion,
            'emotion_probability': emotion_probability
        }
        
        logger.info(f"Generating story with {len(input_data['paintings'])} paintings for user: {input_data['user_name'] or 'anonymous'}")
        if input_data['emotion'] and input_data['emotion_probability'] is not None:
            logger.info(f"Story will incorporate emotion: {input_data['emotion']} ({input_data['emotion_probability']}%)")
        
        # Run Python story generator with secure wrapper
        story_script_path = os.path.join(os.getcwd(), 'story_generation/secure_story_generator.py')
        result = run_python_story_script(story_script_path, input_data)
        
        # Clean up downloaded images
        for painting in paintings_with_images:
            try:
                os.unlink(painting['imagePath'])
                logger.info(f"Cleaned up image: {painting['imageFilename']}")
            except Exception as e:
                logger.error(f"Failed to clean up image {painting['imageFilename']}: {e}")
        
        if result.get('success'):
            logger.info(f"Story generated successfully ({result.get('word_count')} words)")
            return jsonify(result)
        else:
            logger.error(f"Story generation failed: {result.get('error')}")
            return jsonify({
                'error': 'Failed to generate story',
                'message': result.get('error')
            }), 500
        
    except Exception as e:
        logger.error(f"Error generating story: {e}")
        
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

@app.route('/api/health')
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
    
    # Check database if enabled
    if DB_ENABLED:
        try:
            if db.health_check():
                health_data['components']['database'] = 'healthy'
            else:
                health_data['components']['database'] = 'unhealthy'
                health_data['status'] = 'degraded'
        except Exception as e:
            health_data['components']['database'] = f'error: {str(e)}'
            health_data['status'] = 'degraded'
    else:
        health_data['components']['database'] = 'disabled'
    
    # Check uploads directory
    if not os.path.exists(UPLOAD_FOLDER):
        health_data['components']['filesystem'] = 'uploads directory missing'
        health_data['status'] = 'unhealthy'
    
    status_code = 200 if health_data['status'] == 'healthy' else 503
    return jsonify(health_data), status_code

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
