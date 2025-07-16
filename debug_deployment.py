#!/usr/bin/env python3
"""
Debug script to troubleshoot deployment issues
Usage: python3 debug_deployment.py
"""

import os
import sys
import subprocess
from pathlib import Path

def check_path_exists(path, description):
    """Check if a path exists and report status"""
    if os.path.exists(path):
        print(f"✅ {description}: {path}")
        return True
    else:
        print(f"❌ {description}: {path} (NOT FOUND)")
        return False

def check_file_executable(path, description):
    """Check if a file is executable"""
    if os.path.exists(path) and os.access(path, os.X_OK):
        print(f"✅ {description}: {path} (EXECUTABLE)")
        return True
    elif os.path.exists(path):
        print(f"⚠️  {description}: {path} (EXISTS but NOT EXECUTABLE)")
        return False
    else:
        print(f"❌ {description}: {path} (NOT FOUND)")
        return False

def run_command(cmd, description):
    """Run a command and return result"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description}: SUCCESS")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {description}: FAILED")
            print(f"   Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ {description}: ERROR - {e}")
        return False

def debug_deployment():
    """Debug deployment issues"""
    print("🔍 Plot & Palette Deployment Debug Tool")
    print("=" * 50)
    
    # Configuration
    PROJECT_DIR = "/var/www/plot-palette"
    PID_DIR = "/var/run/plot-palette"
    LOG_DIR = "/var/log/plot-palette"
    
    issues = []
    
    # 1. Check project directory
    print("\n📁 Checking Project Structure:")
    if not check_path_exists(PROJECT_DIR, "Project directory"):
        issues.append("Project directory missing")
    
    # 2. Check virtual environment
    print("\n🐍 Checking Python Virtual Environment:")
    venv_path = f"{PROJECT_DIR}/venv"
    if not check_path_exists(venv_path, "Virtual environment"):
        issues.append("Virtual environment missing")
    
    # 3. Check gunicorn binary
    print("\n🚀 Checking Gunicorn:")
    gunicorn_path = f"{PROJECT_DIR}/venv/bin/gunicorn"
    if not check_file_executable(gunicorn_path, "Gunicorn binary"):
        issues.append("Gunicorn binary missing or not executable")
    
    # 4. Check gunicorn config
    print("\n⚙️  Checking Gunicorn Configuration:")
    gunicorn_conf = f"{PROJECT_DIR}/gunicorn.conf.py"
    if not check_path_exists(gunicorn_conf, "Gunicorn config file"):
        issues.append("Gunicorn config file missing")
    
    # 5. Check main application file
    print("\n🎯 Checking Application Files:")
    server_py = f"{PROJECT_DIR}/server.py"
    if not check_path_exists(server_py, "Main application file"):
        issues.append("Main application file missing")
    
    # 6. Check directories
    print("\n📂 Checking Required Directories:")
    check_path_exists(PID_DIR, "PID directory")
    check_path_exists(LOG_DIR, "Log directory")
    check_path_exists(f"{PROJECT_DIR}/uploads", "Uploads directory")
    
    # 7. Check file permissions
    print("\n🔒 Checking File Permissions:")
    run_command(f"ls -la {PROJECT_DIR}/venv/bin/gunicorn", "Gunicorn permissions")
    run_command(f"ls -la {PROJECT_DIR}/server.py", "Server.py permissions")
    
    # 8. Test virtual environment
    print("\n🧪 Testing Virtual Environment:")
    venv_python = f"{PROJECT_DIR}/venv/bin/python3"
    if check_file_executable(venv_python, "Virtual environment Python"):
        run_command(f"{venv_python} --version", "Python version")
        run_command(f"{venv_python} -c 'import flask; print(flask.__version__)'", "Flask import")
        run_command(f"{venv_python} -c 'import gunicorn; print(gunicorn.__version__)'", "Gunicorn import")
    
    # 9. Test gunicorn directly
    print("\n🔧 Testing Gunicorn Directly:")
    if os.path.exists(gunicorn_path):
        run_command(f"cd {PROJECT_DIR} && {gunicorn_path} --version", "Gunicorn version")
        run_command(f"cd {PROJECT_DIR} && {gunicorn_path} --check-config -c gunicorn.conf.py server:app", "Gunicorn config test")
    
    # 10. Check systemd service
    print("\n🔄 Checking SystemD Service:")
    run_command("systemctl is-enabled plot-palette.service", "Service enabled")
    run_command("systemctl show plot-palette.service -p User", "Service user")
    run_command("systemctl show plot-palette.service -p WorkingDirectory", "Service working directory")
    
    # Summary
    print("\n" + "=" * 50)
    if issues:
        print("❌ Issues Found:")
        for i, issue in enumerate(issues, 1):
            print(f"   {i}. {issue}")
        print("\n💡 Suggested fixes:")
        print("   1. Re-run the deployment script: sudo ./deploy.sh")
        print("   2. Check if virtual environment was created properly")
        print("   3. Verify all files were copied to /var/www/plot-palette")
        print("   4. Check file permissions with: sudo chown -R www-data:www-data /var/www/plot-palette")
    else:
        print("✅ No obvious issues found. Check system logs for more details.")
    
    return len(issues) == 0

if __name__ == "__main__":
    success = debug_deployment()
    sys.exit(0 if success else 1) 