#!/usr/bin/env python3
"""
Debug script to test the recommendation script directly
Usage: python3 debug_recommendation_script.py
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def test_recommendation_script_direct():
    """Test the recommendation script directly with venv Python"""
    print("🔍 Testing Recommendation Script Directly")
    print("=" * 50)
    
    # Configuration
    project_dir = "/var/www/plot-palette"
    venv_python = f"{project_dir}/venv/bin/python3"
    script_path = f"{project_dir}/recommendation_service_embedded.py"
    
    # Check if files exist
    if not os.path.exists(venv_python):
        print(f"❌ Virtual environment Python not found: {venv_python}")
        return False
    
    if not os.path.exists(script_path):
        print(f"❌ Recommendation script not found: {script_path}")
        return False
    
    # Test basic Python execution
    print("\n1. Testing basic Python execution:")
    try:
        result = subprocess.run([venv_python, "--version"], capture_output=True, text=True)
        print(f"   Python version: {result.stdout.strip()}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test pandas import
    print("\n2. Testing pandas import:")
    try:
        result = subprocess.run([venv_python, "-c", "import pandas; print(f'pandas {pandas.__version__}')"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"   ✅ {result.stdout.strip()}")
        else:
            print(f"   ❌ pandas import failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test script import (without running main)
    print("\n3. Testing script import:")
    try:
        test_import_cmd = f"""
import sys
sys.path.insert(0, '{project_dir}')
try:
    # Try to import the script module
    exec(open('{script_path}').read().split('if __name__')[0])
    print('Script imports successfully')
except Exception as e:
    print(f'Import error: {{e}}')
    import traceback
    traceback.print_exc()
"""
        result = subprocess.run([venv_python, "-c", test_import_cmd], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"   ✅ {result.stdout.strip()}")
        else:
            print(f"   ❌ Script import failed:")
            print(f"   Error: {result.stderr}")
            print(f"   Output: {result.stdout}")
            return False
    except subprocess.TimeoutExpired:
        print("   ⏰ Script import timed out")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test with a sample image if available
    print("\n4. Testing with sample image:")
    
    # Look for any image file in uploads
    uploads_dir = f"{project_dir}/uploads"
    image_files = []
    if os.path.exists(uploads_dir):
        for file in os.listdir(uploads_dir):
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                image_files.append(os.path.join(uploads_dir, file))
    
    if image_files:
        test_image = image_files[0]
        print(f"   Using test image: {test_image}")
        
        try:
            # Run the script with the test image
            result = subprocess.run([venv_python, script_path, test_image], 
                                  capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print("   ✅ Script executed successfully")
                print(f"   Output length: {len(result.stdout)} characters")
                if len(result.stdout) > 200:
                    print(f"   Output preview: {result.stdout[:200]}...")
                else:
                    print(f"   Output: {result.stdout}")
            else:
                print(f"   ❌ Script failed with exit code: {result.returncode}")
                print(f"   Error: {result.stderr}")
                if result.stdout:
                    print(f"   Output: {result.stdout}")
                return False
                
        except subprocess.TimeoutExpired:
            print("   ⏰ Script execution timed out")
            return False
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    else:
        print("   ⚠️  No test images found in uploads directory")
        print("   Upload a palette image first, then run this test")
    
    return True

def check_data_files():
    """Check if required data files exist"""
    print("\n🗂️  Checking Data Files")
    print("=" * 50)
    
    project_dir = "/var/www/plot-palette"
    
    # Check for common data files in emotions_generation directory (correct location)
    data_files = [
        "interpretable_color_features_cleaned.csv",
        "resampled_emotions_data.csv",
        "final_emotion_model.pkl",
        "final_feature_info.pkl",
        "final_scaler.pkl"
    ]
    
    missing_files = []
    
    # Check emotions_generation directory (where files should be)
    emotions_dir = os.path.join(project_dir, "emotions_generation")
    if os.path.exists(emotions_dir):
        print(f"   📁 emotions_generation directory exists")
        for file in data_files:
            file_path = os.path.join(emotions_dir, file)
            if os.path.exists(file_path):
                size = os.path.getsize(file_path)
                print(f"   ✅ emotions_generation/{file} ({size:,} bytes)")
            else:
                print(f"   ❌ emotions_generation/{file} - NOT FOUND")
                missing_files.append(file)
    else:
        print(f"   ❌ emotions_generation directory - NOT FOUND")
        missing_files.extend(data_files)
    
    return len(missing_files) == 0

def check_permissions():
    """Check file permissions"""
    print("\n🔒 Checking Permissions")
    print("=" * 50)
    
    project_dir = "/var/www/plot-palette"
    
    # Check key files
    files_to_check = [
        "recommendation_service_embedded.py",
        "venv/bin/python3",
        "uploads"
    ]
    
    for file in files_to_check:
        file_path = os.path.join(project_dir, file)
        if os.path.exists(file_path):
            stat = os.stat(file_path)
            permissions = oct(stat.st_mode)[-3:]
            print(f"   {file}: {permissions}")
        else:
            print(f"   ❌ {file} - NOT FOUND")

def main():
    """Main debugging function"""
    print("🧪 Recommendation Script Debug Tool")
    print("=" * 50)
    
    success = True
    
    # Test the recommendation script
    if not test_recommendation_script_direct():
        success = False
    
    # Check data files
    if not check_data_files():
        success = False
    
    # Check permissions
    check_permissions()
    
    # Summary
    print("\n" + "=" * 50)
    if success:
        print("✅ All tests passed!")
        print("💡 The recommendation script should work correctly")
    else:
        print("❌ Some tests failed")
        print("💡 Check the errors above and fix the issues")
    
    print("\n📋 Common fixes:")
    print("   - Ensure all data files are present")
    print("   - Check file permissions")
    print("   - Verify virtual environment has all packages")
    print("   - Check if images are accessible")

if __name__ == "__main__":
    main() 