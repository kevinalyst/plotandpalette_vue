from flask import Flask, request, jsonify
import subprocess
import json
import sys
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route("/health")
def health_check():
    return {"status": "healthy", "service": "story-generation"}

@app.route("/test-files", methods=["POST"])
def test_files():
    """Test endpoint to check if uploaded files are accessible"""
    try:
        data = request.get_json()
        paintings = data.get('paintings', [])
        
        file_status = []
        for i, painting in enumerate(paintings):
            image_path = painting.get('imagePath', '')
            exists = os.path.exists(image_path) if image_path else False
            file_status.append({
                'index': i,
                'path': image_path,
                'exists': exists,
                'size': os.path.getsize(image_path) if exists else 0
            })
        
        return {
            'success': True,
            'file_status': file_status,
            'uploads_dir_exists': os.path.exists('/app/uploads'),
            'uploads_contents': os.listdir('/app/uploads') if os.path.exists('/app/uploads') else []
        }
    except Exception as e:
        return {"success": False, "error": str(e)}, 500

@app.route("/generate", methods=["POST"])
def generate_story():
    try:
        data = request.get_json()
        logger.info(f"📖 Story generation request received")
        logger.info(f"📖 Data keys: {list(data.keys()) if data else 'None'}")
        
        if data and 'paintings' in data:
            paintings = data['paintings']
            logger.info(f"📖 Number of paintings: {len(paintings)}")
            for i, painting in enumerate(paintings):
                image_path = painting.get('imagePath', 'No path')
                exists = os.path.exists(image_path) if image_path != 'No path' else False
                logger.info(f"📖 Painting {i+1}: {painting.get('title', 'Unknown')} - Path: {image_path} - Exists: {exists}")
        
        # Call the secure story generator directly
        logger.info(f"📖 Calling secure_story_generator.py (OpenAI backend)...")
        result = subprocess.run(
            [sys.executable, "secure_story_generator.py", json.dumps(data)],
            capture_output=True,
            text=True,
            timeout=180
        )
        
        logger.info(f"📖 Script return code: {result.returncode}")
        logger.info(f"📖 Script stdout length: {len(result.stdout)}")
        logger.info(f"📖 Script stderr length: {len(result.stderr)}")
        
        # Log stderr regardless of return code (contains validation details)
        if result.stderr:
            logger.info(f"📖 Script stderr: {result.stderr}")
        
        if result.returncode == 0:
            try:
                response_data = json.loads(result.stdout)
                logger.info(f"📖 Story generation result: {response_data.get('success', 'Unknown')}")
                return response_data
            except json.JSONDecodeError as e:
                logger.error(f"📖 Failed to parse stdout as JSON: {e}")
                logger.error(f"📖 Raw stdout: {result.stdout}")
                return {"success": False, "error": f"Invalid JSON response: {str(e)}"}, 500
        else:
            logger.error(f"📖 Script failed with return code {result.returncode}")
            return {"success": False, "error": result.stderr or "Script execution failed"}, 500
            
    except Exception as e:
        logger.error(f"📖 Exception in generate_story: {e}")
        return {"success": False, "error": str(e)}, 500

if __name__ == "__main__":
    logger.info(f"📖 Starting story API service...")
    # Cloud Run sidecar port remains 5002 (Nginx reverse proxies over localhost)
    app.run(host="0.0.0.0", port=5002)