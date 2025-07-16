#!/usr/bin/env python3
"""
Debug script to test systemd service execution
Usage: python3 debug_systemd_service.py
"""

import os
import sys
import subprocess
import pwd
import grp
from pathlib import Path

def test_as_user(username, command, working_dir):
    """Test running a command as a specific user"""
    try:
        # Get user info
        user_info = pwd.getpwnam(username)
        group_info = grp.getgrgid(user_info.pw_gid)
        
        print(f"🔍 Testing as user: {username} (uid: {user_info.pw_uid}, gid: {user_info.pw_gid})")
        print(f"   Group: {group_info.gr_name}")
        print(f"   Home: {user_info.pw_dir}")
        print(f"   Shell: {user_info.pw_shell}")
        print(f"   Working dir: {working_dir}")
        print(f"   Command: {command}")
        print("-" * 50)
        
        # Try to run the command as the user
        result = subprocess.run([
            'sudo', '-u', username, '-g', group_info.gr_name,
            'bash', '-c', f'cd {working_dir} && {command}'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Command executed successfully")
            if result.stdout:
                print(f"   Output: {result.stdout.strip()}")
        else:
            print("❌ Command failed")
            print(f"   Exit code: {result.returncode}")
            if result.stderr:
                print(f"   Error: {result.stderr.strip()}")
            if result.stdout:
                print(f"   Output: {result.stdout.strip()}")
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("⏰ Command timed out")
        return False
    except Exception as e:
        print(f"❌ Error testing command: {e}")
        return False

def check_systemd_service():
    """Check systemd service configuration"""
    print("🔄 Checking SystemD Service Configuration:")
    print("-" * 50)
    
    service_file = "/etc/systemd/system/plot-palette.service"
    
    if os.path.exists(service_file):
        print("✅ Service file exists")
        with open(service_file, 'r') as f:
            content = f.read()
            print("Service file content:")
            print(content)
    else:
        print("❌ Service file not found")
        return False
    
    return True

def test_manual_startup():
    """Test manual startup simulation"""
    print("\n🧪 Testing Manual Startup Simulation:")
    print("-" * 50)
    
    PROJECT_DIR = "/var/www/plot-palette"
    
    # Test components step by step
    steps = [
        ("Check working directory", f"ls -la {PROJECT_DIR}"),
        ("Check virtual environment", f"ls -la {PROJECT_DIR}/venv/bin/"),
        ("Check gunicorn binary", f"file {PROJECT_DIR}/venv/bin/gunicorn"),
        ("Test gunicorn version", f"{PROJECT_DIR}/venv/bin/gunicorn --version"),
        ("Check server.py", f"ls -la {PROJECT_DIR}/server.py"),
        ("Check gunicorn config", f"ls -la {PROJECT_DIR}/gunicorn.conf.py"),
        ("Test Python import", f"{PROJECT_DIR}/venv/bin/python3 -c 'import server; print(\"Server import OK\")'"),
        ("Test config validation", f"{PROJECT_DIR}/venv/bin/gunicorn --check-config -c {PROJECT_DIR}/gunicorn.conf.py server:app"),
    ]
    
    print("Testing as www-data user:")
    for step_name, command in steps:
        print(f"\n{step_name}:")
        success = test_as_user("www-data", command, PROJECT_DIR)
        if not success:
            print(f"❌ Failed at step: {step_name}")
            return False
    
    return True

def test_gunicorn_startup():
    """Test actual gunicorn startup"""
    print("\n🚀 Testing Gunicorn Startup:")
    print("-" * 50)
    
    PROJECT_DIR = "/var/www/plot-palette"
    
    # Test the exact command from systemd service
    gunicorn_cmd = f"{PROJECT_DIR}/venv/bin/gunicorn -c {PROJECT_DIR}/gunicorn.conf.py server:app"
    
    print("Testing gunicorn startup (will timeout after 10 seconds):")
    try:
        result = subprocess.run([
            'sudo', '-u', 'www-data', '-g', 'www-data',
            'bash', '-c', f'cd {PROJECT_DIR} && timeout 10s {gunicorn_cmd}'
        ], capture_output=True, text=True, timeout=15)
        
        if result.returncode == 124:  # timeout exit code
            print("✅ Gunicorn started successfully (timed out as expected)")
            return True
        elif result.returncode == 0:
            print("✅ Gunicorn started and exited normally")
            return True
        else:
            print(f"❌ Gunicorn failed with exit code: {result.returncode}")
            if result.stderr:
                print(f"   Error: {result.stderr}")
            if result.stdout:
                print(f"   Output: {result.stdout}")
            return False
            
    except subprocess.TimeoutExpired:
        print("✅ Gunicorn started successfully (process running)")
        return True
    except Exception as e:
        print(f"❌ Error testing gunicorn: {e}")
        return False

def debug_systemd_service():
    """Main debugging function"""
    print("🔍 SystemD Service Debug Tool")
    print("=" * 50)
    
    issues = []
    
    # Check service configuration
    if not check_systemd_service():
        issues.append("SystemD service configuration issue")
    
    # Test manual startup
    if not test_manual_startup():
        issues.append("Manual startup test failed")
    
    # Test gunicorn startup
    if not test_gunicorn_startup():
        issues.append("Gunicorn startup test failed")
    
    # Summary
    print("\n" + "=" * 50)
    if issues:
        print("❌ Issues Found:")
        for i, issue in enumerate(issues, 1):
            print(f"   {i}. {issue}")
        
        print("\n💡 Suggested fixes:")
        print("   1. Check file permissions: sudo chown -R www-data:www-data /var/www/plot-palette")
        print("   2. Make gunicorn executable: sudo chmod +x /var/www/plot-palette/venv/bin/gunicorn")
        print("   3. Check environment variables in systemd service")
        print("   4. Try starting manually: sudo -u www-data /var/www/plot-palette/venv/bin/gunicorn -c /var/www/plot-palette/gunicorn.conf.py server:app")
        print("   5. Check systemd journal: sudo journalctl -xeu plot-palette.service")
    else:
        print("✅ No issues found with manual testing")
        print("💡 The issue might be systemd-specific. Try:")
        print("   1. sudo systemctl daemon-reload")
        print("   2. sudo systemctl restart plot-palette.service")
    
    return len(issues) == 0

if __name__ == "__main__":
    success = debug_systemd_service()
    sys.exit(0 if success else 1) 