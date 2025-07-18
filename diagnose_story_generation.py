#!/usr/bin/env python3
"""
Story Generation Diagnostic Script
Comprehensive debugging tool for Plot & Palette story generation issues
"""
import os
import sys
import subprocess
import json
import traceback
from pathlib import Path

def print_header(title):
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print(f"{'='*60}")

def print_status(status, message):
    emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
    print(f"{emoji} {status}: {message}")

def run_command(command, description=""):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return False, "", f"Command timed out: {command}"
    except Exception as e:
        return False, "", str(e)

def check_environment():
    """Check basic environment setup"""
    print_header("Environment Check")
    
    # Check current directory
    current_dir = os.getcwd()
    print_status("INFO", f"Current directory: {current_dir}")
    
    # Check if we're in the right directory
    if "/var/www/plot-palette" in current_dir:
        print_status("PASS", "Running from correct project directory")
    else:
        print_status("WARN", "Not in /var/www/plot-palette directory")
        
    # Check Python version
    python_version = sys.version
    print_status("INFO", f"Python version: {python_version}")
    
    # Check story_generation directory
    story_dir = Path("story_generation")
    if story_dir.exists():
        print_status("PASS", "story_generation directory exists")
    else:
        print_status("FAIL", "story_generation directory not found")
        return False
    
    return True

def check_file_permissions():
    """Check file permissions for story generation"""
    print_header("File Permissions Check")
    
    paths_to_check = [
        "story_generation/",
        "story_generation/.env",
        "story_generation/image_story_generator.py",
        "story_generation/secure_story_generator.py",
        "uploads/"
    ]
    
    for path in paths_to_check:
        if os.path.exists(path):
            stat_info = os.stat(path)
            permissions = oct(stat_info.st_mode)[-3:]
            print_status("INFO", f"{path}: permissions {permissions}")
        else:
            print_status("FAIL", f"{path}: does not exist")

def check_environment_variables():
    """Check environment variables and .env file"""
    print_header("Environment Variables Check")
    
    # Check .env file
    env_file = Path("story_generation/.env")
    if env_file.exists():
        print_status("PASS", ".env file exists")
        try:
            with open(env_file, 'r') as f:
                env_content = f.read()
            
            if "ANTHROPIC_API_KEY" in env_content:
                # Check if API key has content (not just the variable name)
                for line in env_content.split('\n'):
                    if line.startswith('ANTHROPIC_API_KEY=') and len(line.split('=', 1)) > 1:
                        api_key_value = line.split('=', 1)[1].strip()
                        if api_key_value and api_key_value != "your_api_key_here":
                            print_status("PASS", "ANTHROPIC_API_KEY is set in .env")
                        else:
                            print_status("FAIL", "ANTHROPIC_API_KEY is empty or placeholder")
                        break
                else:
                    print_status("FAIL", "ANTHROPIC_API_KEY not properly set")
            else:
                print_status("FAIL", "ANTHROPIC_API_KEY not found in .env")
                
        except Exception as e:
            print_status("FAIL", f"Error reading .env file: {e}")
    else:
        print_status("FAIL", ".env file not found")

def check_python_packages():
    """Check if required Python packages are installed"""
    print_header("Python Packages Check")
    
    # Use the virtual environment python
    venv_python = "venv/bin/python3" if os.path.exists("venv/bin/python3") else "python3"
    
    required_packages = [
        "anthropic",
        "requests", 
        "pillow",
        "python-dotenv"
    ]
    
    for package in required_packages:
        import_name = package.replace("-", "_")
        success, stdout, stderr = run_command(f"{venv_python} -c \"import {import_name}; print({import_name}.__version__)\"")
        if success:
            print_status("PASS", f"{package}: {stdout}")
        else:
            print_status("FAIL", f"{package}: not installed or import error")
            print(f"   Error: {stderr}")

def test_imports():
    """Test importing story generation modules"""
    print_header("Import Test")
    
    venv_python = "venv/bin/python3" if os.path.exists("venv/bin/python3") else "python3"
    
    test_scripts = [
        ("story_generation.image_story_generator", "Main story generator"),
        ("story_generation.secure_story_generator", "Secure story generator")
    ]
    
    for module, description in test_scripts:
        success, stdout, stderr = run_command(f"cd /var/www/plot-palette && {venv_python} -c 'import {module}; print(\"Import successful\")'")
        if success:
            print_status("PASS", f"{description}: Import successful")
        else:
            print_status("FAIL", f"{description}: Import failed")
            print(f"   Error: {stderr}")

def test_api_connectivity():
    """Test Claude API connectivity"""
    print_header("API Connectivity Test")
    
    venv_python = "venv/bin/python3" if os.path.exists("venv/bin/python3") else "python3"
    
    test_code = """
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('story_generation/.env')

api_key = os.getenv('ANTHROPIC_API_KEY')
if not api_key:
    print("FAIL: No API key found")
    exit(1)

if api_key == 'your_api_key_here':
    print("FAIL: API key is placeholder")
    exit(1)

try:
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)
    
    # Simple test call
    response = client.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=10,
        messages=[{"role": "user", "content": "Hello"}]
    )
    print("PASS: API connection successful")
except Exception as e:
    print(f"FAIL: API connection failed - {e}")
"""
    
    success, stdout, stderr = run_command(f"cd /var/www/plot-palette && {venv_python} -c '{test_code}'")
    if "PASS" in stdout:
        print_status("PASS", "Claude API connectivity test passed")
    else:
        print_status("FAIL", "Claude API connectivity test failed")
        print(f"   Output: {stdout}")
        print(f"   Error: {stderr}")

def test_story_generation_direct():
    """Test story generation script directly"""
    print_header("Direct Story Generation Test")
    
    venv_python = "venv/bin/python3" if os.path.exists("venv/bin/python3") else "python3"
    
    # Create test data
    test_paintings = [
        "https://uploads0.wikiart.org/images/test1.jpg",
        "https://uploads0.wikiart.org/images/test2.jpg", 
        "https://uploads0.wikiart.org/images/test3.jpg"
    ]
    
    test_emotion = "happiness"
    test_character = "1"
    
    test_command = f"""
cd /var/www/plot-palette && {venv_python} -c "
import sys
sys.path.append('story_generation')
from image_story_generator import generate_story

try:
    result = generate_story({test_paintings}, '{test_emotion}', '{test_character}')
    print('PASS: Story generation function works')
    print(f'Result type: ' + str(type(result)))
except Exception as e:
    print(f'FAIL: Story generation failed - ' + str(e))
    import traceback
    traceback.print_exc()
"
"""
    
    success, stdout, stderr = run_command(test_command)
    if "PASS" in stdout:
        print_status("PASS", "Direct story generation test passed")
    else:
        print_status("FAIL", "Direct story generation test failed")
        print(f"   Output: {stdout}")
        print(f"   Error: {stderr}")

def check_service_logs():
    """Check recent service logs for story generation errors"""
    print_header("Service Logs Check")
    
    success, stdout, stderr = run_command("sudo journalctl -u plot-palette.service -n 20 | grep -i story")
    if success and stdout:
        print_status("INFO", "Recent story-related logs:")
        for line in stdout.split('\n'):
            print(f"   {line}")
    else:
        print_status("INFO", "No recent story-related logs found")

def auto_fix_common_issues():
    """Attempt to automatically fix common issues"""
    print_header("Auto-Fix Common Issues")
    
    venv_python = "venv/bin/python3" if os.path.exists("venv/bin/python3") else "python3"
    
    # Fix 1: Install missing packages
    print("🔧 Installing/updating required packages...")
    success, stdout, stderr = run_command(f"{venv_python} -m pip install anthropic requests Pillow python-dotenv --upgrade")
    if success:
        print_status("PASS", "Packages installed/updated successfully")
    else:
        print_status("FAIL", f"Package installation failed: {stderr}")
    
    # Fix 2: Fix permissions
    print("🔧 Fixing file permissions...")
    success, stdout, stderr = run_command("sudo chown -R www-data:www-data story_generation/")
    if success:
        print_status("PASS", "File permissions fixed")
    else:
        print_status("WARN", f"Could not fix permissions: {stderr}")
    
    # Fix 3: Create .env if missing
    if not os.path.exists("story_generation/.env"):
        print("🔧 Creating .env template...")
        try:
            with open("story_generation/.env", "w") as f:
                f.write("ANTHROPIC_API_KEY=your_api_key_here\n")
            print_status("PASS", ".env template created (you need to add your API key)")
        except Exception as e:
            print_status("FAIL", f"Could not create .env: {e}")

def main():
    """Main diagnostic function"""
    print("🩺 Plot & Palette Story Generation Diagnostic Tool")
    print("=" * 60)
    
    # Change to project directory if not already there
    if not os.getcwd().endswith("plot-palette"):
        try:
            os.chdir("/var/www/plot-palette")
            print(f"Changed to: {os.getcwd()}")
        except:
            print("❌ Could not change to /var/www/plot-palette")
            return
    
    # Run all diagnostic checks
    checks = [
        check_environment,
        check_file_permissions,
        check_environment_variables,
        check_python_packages,
        test_imports,
        test_api_connectivity,
        test_story_generation_direct,
        check_service_logs
    ]
    
    for check in checks:
        try:
            check()
        except Exception as e:
            print_status("FAIL", f"Check failed with exception: {e}")
            traceback.print_exc()
    
    # Offer auto-fix
    print("\n" + "="*60)
    response = input("🔧 Would you like to attempt auto-fixes? (y/n): ").lower()
    if response == 'y':
        auto_fix_common_issues()
    
    print("\n" + "="*60)
    print("✅ Diagnostic complete!")
    print("📋 Summary: Check the output above for any FAIL status items")
    print("🔧 If issues persist, check the specific error messages and fix manually")

if __name__ == "__main__":
    main() 