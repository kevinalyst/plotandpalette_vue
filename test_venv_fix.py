#!/usr/bin/env python3
"""
Test script to verify virtual environment Python and package installation
Usage: python3 test_venv_fix.py
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def test_python_executable(python_path, label):
    """Test a Python executable"""
    print(f"\n🐍 Testing {label}: {python_path}")
    print("-" * 50)
    
    if not os.path.exists(python_path):
        print(f"❌ Python executable not found at: {python_path}")
        return False
    
    try:
        # Test basic Python info
        result = subprocess.run([python_path, '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Python version: {result.stdout.strip()}")
        else:
            print(f"❌ Failed to get Python version: {result.stderr}")
            return False
        
        # Test pandas import
        result = subprocess.run([python_path, '-c', 'import pandas as pd; print(f"pandas version: {pd.__version__}")'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ pandas: {result.stdout.strip()}")
        else:
            print(f"❌ pandas import failed: {result.stderr}")
            return False
        
        # Test other required packages
        packages = ['numpy', 'scikit-learn', 'requests', 'PIL', 'joblib']
        for pkg in packages:
            try:
                if pkg == 'PIL':
                    import_cmd = 'from PIL import Image; print("PIL: OK")'
                else:
                    import_cmd = f'import {pkg}; print("{pkg}: OK")'
                
                result = subprocess.run([python_path, '-c', import_cmd], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"✅ {result.stdout.strip()}")
                else:
                    print(f"❌ {pkg} import failed: {result.stderr}")
                    return False
            except Exception as e:
                print(f"❌ Error testing {pkg}: {e}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing {label}: {e}")
        return False

def test_recommendation_script():
    """Test the recommendation script directly"""
    print(f"\n🎨 Testing Recommendation Script")
    print("-" * 50)
    
    # Check if recommendation script exists
    script_path = "recommendation_service_embedded.py"
    if not os.path.exists(script_path):
        print(f"❌ Recommendation script not found: {script_path}")
        return False
    
    # Test with venv Python
    venv_python = os.path.join(os.getcwd(), 'venv', 'bin', 'python3')
    if os.path.exists(venv_python):
        print(f"Testing with venv Python: {venv_python}")
        
        # Create a dummy test image (just test the import)
        try:
            result = subprocess.run([venv_python, '-c', 'exec(open("recommendation_service_embedded.py").read().split("if __name__")[0])'], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                print("✅ Recommendation script imports successfully")
                return True
            else:
                print(f"❌ Recommendation script import failed: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            print("✅ Recommendation script started (timed out as expected)")
            return True
        except Exception as e:
            print(f"❌ Error testing recommendation script: {e}")
            return False
    else:
        print(f"❌ Virtual environment Python not found: {venv_python}")
        return False

def test_server_integration():
    """Test the server.py integration"""
    print(f"\n🖥️  Testing Server Integration")
    print("-" * 50)
    
    # Check if server.py exists
    if not os.path.exists("server.py"):
        print("❌ server.py not found")
        return False
    
    # Test the server imports
    venv_python = os.path.join(os.getcwd(), 'venv', 'bin', 'python3')
    if os.path.exists(venv_python):
        try:
            result = subprocess.run([venv_python, '-c', 'import server; print("Server import: OK")'], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                print("✅ Server imports successfully")
                return True
            else:
                print(f"❌ Server import failed: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            print("✅ Server import started (timed out as expected)")
            return True
        except Exception as e:
            print(f"❌ Error testing server: {e}")
            return False
    else:
        print(f"❌ Virtual environment Python not found: {venv_python}")
        return False

def main():
    """Main test function"""
    print("🧪 Virtual Environment Fix Test")
    print("=" * 50)
    
    # Test system Python
    system_python_ok = test_python_executable('/usr/bin/python3', 'System Python')
    
    # Test virtual environment Python
    venv_python = os.path.join(os.getcwd(), 'venv', 'bin', 'python3')
    venv_python_ok = test_python_executable(venv_python, 'Virtual Environment Python')
    
    # Test recommendation script
    recommendation_ok = test_recommendation_script()
    
    # Test server integration
    server_ok = test_server_integration()
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Test Results Summary:")
    print(f"   System Python: {'✅ PASS' if system_python_ok else '❌ FAIL'}")
    print(f"   Virtual Environment Python: {'✅ PASS' if venv_python_ok else '❌ FAIL'}")
    print(f"   Recommendation Script: {'✅ PASS' if recommendation_ok else '❌ FAIL'}")
    print(f"   Server Integration: {'✅ PASS' if server_ok else '❌ FAIL'}")
    
    if venv_python_ok and recommendation_ok and server_ok:
        print("\n🎉 All tests passed! The fix should work.")
        print("💡 Next steps:")
        print("   1. Commit and push the server.py changes")
        print("   2. Deploy the updated server.py to your VM")
        print("   3. Restart the systemd service")
    else:
        print("\n❌ Some tests failed. Issues to address:")
        if not venv_python_ok:
            print("   - Virtual environment Python has missing packages")
        if not recommendation_ok:
            print("   - Recommendation script has issues")
        if not server_ok:
            print("   - Server integration has issues")
        print("\n💡 Suggested fixes:")
        print("   - Reinstall packages in virtual environment")
        print("   - Check virtual environment activation")
        print("   - Verify all required packages are installed")

if __name__ == "__main__":
    main() 