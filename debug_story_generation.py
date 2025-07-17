#!/usr/bin/env python3
"""
Debug script for story generation issues
Usage: python3 debug_story_generation.py
"""

import os
import sys
import subprocess
import json
from datetime import datetime
from pathlib import Path

def test_environment():
    """Test the environment setup for story generation"""
    print("🧪 Testing Story Generation Environment")
    print("=" * 50)
    
    issues = []
    
    # 1. Check if story_generation directory exists
    story_dir = "story_generation"
    if os.path.exists(story_dir):
        print(f"✅ story_generation directory exists")
    else:
        print(f"❌ story_generation directory missing")
        issues.append("story_generation directory not found")
        return issues
    
    # 2. Check required Python files
    required_files = [
        "story_generation/secure_story_generator.py",
        "story_generation/image_story_generator.py",
        "story_generation/requirements.txt"
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} exists")
        else:
            print(f"❌ {file} missing")
            issues.append(f"Missing file: {file}")
    
    # 3. Check .env file
    env_file = "story_generation/.env"
    if os.path.exists(env_file):
        print(f"✅ .env file exists")
        # Check if it has CLAUDE_API_KEY
        try:
            with open(env_file, 'r') as f:
                content = f.read()
                if 'CLAUDE_API_KEY' in content:
                    print(f"✅ CLAUDE_API_KEY found in .env")
                else:
                    print(f"❌ CLAUDE_API_KEY missing from .env")
                    issues.append("CLAUDE_API_KEY missing from .env")
        except Exception as e:
            print(f"❌ Error reading .env file: {e}")
            issues.append(f"Error reading .env: {e}")
    else:
        print(f"❌ .env file missing")
        issues.append(".env file not found")
    
    return issues

def test_python_dependencies():
    """Test if required Python packages are installed"""
    print("\n📦 Testing Python Dependencies")
    print("=" * 50)
    
    issues = []
    required_packages = ['anthropic', 'python-dotenv', 'PIL']
    
    for package in required_packages:
        try:
            if package == 'PIL':
                import PIL
                print(f"✅ {package} (Pillow) is installed")
            else:
                __import__(package)
                print(f"✅ {package} is installed")
        except ImportError:
            print(f"❌ {package} is NOT installed")
            issues.append(f"Missing package: {package}")
    
    return issues

def test_story_script_execution():
    """Test the story generation script directly"""
    print("\n🎭 Testing Story Script Execution")
    print("=" * 50)
    
    # Create sample input data
    sample_data = {
        "paintings": [
            {
                "url": "https://example.com/painting1.jpg",
                "title": "Test Painting 1",
                "artist": "Test Artist 1",
                "year": "2000",
                "imagePath": "/tmp/test1.jpg"
            },
            {
                "url": "https://example.com/painting2.jpg", 
                "title": "Test Painting 2",
                "artist": "Test Artist 2",
                "year": "2001",
                "imagePath": "/tmp/test2.jpg"
            },
            {
                "url": "https://example.com/painting3.jpg",
                "title": "Test Painting 3", 
                "artist": "Test Artist 3",
                "year": "2002",
                "imagePath": "/tmp/test3.jpg"
            }
        ],
        "narrative_style": "historian",
        "user_name": "TestUser",
        "emotion": "happiness",
        "emotion_probability": 75.0
    }
    
    # Create dummy image files for testing
    for i in range(3):
        dummy_file = f"/tmp/test{i+1}.jpg"
        try:
            with open(dummy_file, 'w') as f:
                f.write("dummy image data")
            print(f"✅ Created dummy image: {dummy_file}")
        except Exception as e:
            print(f"❌ Failed to create dummy image {dummy_file}: {e}")
            return [f"Failed to create test files: {e}"]
    
    issues = []
    
    # Test 1: Basic script import test
    print(f"\n1. Testing basic script import...")
    try:
        result = subprocess.run([
            'python3', '-c', 
            'import sys; sys.path.append("story_generation"); import secure_story_generator; print("Import successful")'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print(f"✅ Script imports successfully")
        else:
            print(f"❌ Script import failed:")
            print(f"   Error: {result.stderr}")
            issues.append(f"Script import failed: {result.stderr}")
    except Exception as e:
        print(f"❌ Script import test failed: {e}")
        issues.append(f"Script import test error: {e}")
    
    # Test 2: Full script execution test
    print(f"\n2. Testing full script execution...")
    try:
        script_path = "story_generation/secure_story_generator.py"
        input_json = json.dumps(sample_data)
        
        result = subprocess.run([
            'python3', script_path, input_json
        ], capture_output=True, text=True, timeout=60)
        
        print(f"   Exit code: {result.returncode}")
        if result.stdout:
            print(f"   Stdout length: {len(result.stdout)} characters")
            try:
                # Try to parse as JSON
                output_data = json.loads(result.stdout)
                if output_data.get('success'):
                    print(f"✅ Story generation test successful")
                else:
                    print(f"❌ Story generation failed: {output_data.get('error')}")
                    issues.append(f"Story generation failed: {output_data.get('error')}")
            except json.JSONDecodeError:
                print(f"❌ Invalid JSON output")
                print(f"   Raw output preview: {result.stdout[:200]}...")
                issues.append("Invalid JSON output from story script")
        else:
            print(f"❌ No stdout output")
            issues.append("No output from story script")
        
        if result.stderr:
            print(f"   Stderr: {result.stderr}")
    
    except subprocess.TimeoutExpired:
        print(f"❌ Script execution timed out")
        issues.append("Script execution timeout")
    except Exception as e:
        print(f"❌ Script execution failed: {e}")
        issues.append(f"Script execution error: {e}")
    
    # Cleanup dummy files
    for i in range(3):
        dummy_file = f"/tmp/test{i+1}.jpg"
        try:
            os.unlink(dummy_file)
        except:
            pass
    
    return issues

def test_server_integration():
    """Test how the server calls the story generation"""
    print("\n🖥️  Testing Server Integration")
    print("=" * 50)
    
    # Check if server.py has the correct paths and function
    if not os.path.exists("server.py"):
        print(f"❌ server.py not found")
        return ["server.py not found"]
    
    # Look for the story generation function in server.py
    try:
        with open("server.py", 'r') as f:
            content = f.read()
            
        if 'run_python_story_script' in content:
            print(f"✅ run_python_story_script function found in server.py")
        else:
            print(f"❌ run_python_story_script function not found")
            return ["run_python_story_script function missing"]
        
        if 'story_generation/secure_story_generator.py' in content:
            print(f"✅ Story script path found in server.py")
        else:
            print(f"❌ Story script path not found in server.py")
            return ["Story script path missing in server.py"]
        
        print(f"✅ Server integration looks correct")
        return []
        
    except Exception as e:
        print(f"❌ Error checking server.py: {e}")
        return [f"Error checking server.py: {e}"]

def test_virtual_environment():
    """Test if story generation works in virtual environment"""
    print("\n🐍 Testing Virtual Environment")
    print("=" * 50)
    
    issues = []
    
    # Check if we're in a virtual environment
    venv_python = "/var/www/plot-palette/venv/bin/python3"
    if os.path.exists(venv_python):
        print(f"✅ Virtual environment Python found: {venv_python}")
        
        # Test if anthropic is installed in venv
        try:
            result = subprocess.run([
                venv_python, '-c', 'import anthropic; print("anthropic available")'
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print(f"✅ anthropic package available in venv")
            else:
                print(f"❌ anthropic package missing in venv")
                print(f"   Error: {result.stderr}")
                issues.append("anthropic package missing in virtual environment")
        except Exception as e:
            print(f"❌ Error testing venv packages: {e}")
            issues.append(f"Error testing venv: {e}")
    else:
        print(f"⚠️  Virtual environment not found at {venv_python}")
        print(f"   Using system Python instead")
    
    return issues

def create_fix_script():
    """Create a script to fix common issues"""
    print("\n🔧 Creating Fix Script")
    print("=" * 50)
    
    fix_script = """#!/bin/bash
# Fix script for story generation issues

echo "🔧 Fixing Story Generation Issues..."

# 1. Install required packages
echo "Installing required packages..."
pip install anthropic python-dotenv Pillow

# 2. Create .env file if missing
if [ ! -f "story_generation/.env" ]; then
    echo "Creating .env file..."
    cd story_generation
    python3 setup_env.py
    cd ..
fi

# 3. Set proper permissions
chmod +x story_generation/*.py

# 4. Test the installation
echo "Testing story generation..."
python3 debug_story_generation.py

echo "✅ Fix script completed"
"""
    
    with open("fix_story_generation.sh", 'w') as f:
        f.write(fix_script)
    
    os.chmod("fix_story_generation.sh", 0o755)
    print(f"✅ Created fix_story_generation.sh")
    print(f"   Run: ./fix_story_generation.sh")

def main():
    """Main debugging function"""
    print("🧪 Story Generation Debug Suite")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 60)
    
    all_issues = []
    
    # Run all tests
    all_issues.extend(test_environment())
    all_issues.extend(test_python_dependencies())
    all_issues.extend(test_story_script_execution())
    all_issues.extend(test_server_integration())
    all_issues.extend(test_virtual_environment())
    
    # Summary
    print("\n" + "=" * 60)
    if all_issues:
        print("❌ Issues Found:")
        for i, issue in enumerate(all_issues, 1):
            print(f"   {i}. {issue}")
        
        print("\n💡 Common Fixes:")
        print("   1. Install missing packages: pip install anthropic python-dotenv Pillow")
        print("   2. Create .env file: cd story_generation && python3 setup_env.py")
        print("   3. Check Claude API key in .env file")
        print("   4. Ensure proper file permissions")
        
        create_fix_script()
    else:
        print("✅ All tests passed! Story generation should work correctly.")
    
    print(f"\n📋 Next steps:")
    print("   1. Fix any issues identified above")
    print("   2. Test story generation directly: python3 story_generation/secure_story_generator.py '{...}'")
    print("   3. Restart the plot-palette service")
    print("   4. Test the web application story generation")

if __name__ == "__main__":
    main() 