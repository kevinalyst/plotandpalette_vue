#!/usr/bin/env python3
"""
Setup script for story generation environment
Creates .env file and installs required packages
"""
import os
import subprocess
import sys

def create_env_file():
    """Create .env file with API key placeholder"""
    env_path = "story_generation/.env"
    
    if os.path.exists(env_path):
        print(f"✅ {env_path} already exists")
        
        # Check if API key is set
        with open(env_path, 'r') as f:
            content = f.read()
        
        if "ANTHROPIC_API_KEY=" in content and "your_api_key_here" not in content:
            print("✅ ANTHROPIC_API_KEY appears to be set")
        else:
            print("⚠️  ANTHROPIC_API_KEY needs to be set in .env file")
    else:
        print(f"Creating {env_path}...")
        with open(env_path, 'w') as f:
            f.write("ANTHROPIC_API_KEY=your_api_key_here\n")
        print(f"✅ Created {env_path} - please update with your actual API key")

def install_packages():
    """Install required packages in virtual environment"""
    venv_python = "venv/bin/python3" if os.path.exists("venv/bin/python3") else "python3"
    
    packages = [
        "anthropic>=0.3.0",
        "python-dotenv>=0.19.0", 
        "Pillow>=10.0.0"
    ]
    
    for package in packages:
        print(f"Installing {package}...")
        try:
            subprocess.run([venv_python, "-m", "pip", "install", package], 
                         check=True, capture_output=True)
            print(f"✅ {package} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package}: {e}")

def fix_permissions():
    """Fix file permissions for story generation"""
    try:
        subprocess.run(["sudo", "chown", "-R", "www-data:www-data", "story_generation/"], 
                      check=True, capture_output=True)
        print("✅ File permissions fixed")
    except subprocess.CalledProcessError:
        print("⚠️  Could not fix permissions (you may need to run as sudo)")

def main():
    """Main setup function"""
    print("🔧 Plot & Palette Story Generation Setup")
    print("=" * 50)
    
    # Change to project directory if needed
    if not os.getcwd().endswith("plot-palette"):
        try:
            os.chdir("/var/www/plot-palette")
            print(f"Changed to: {os.getcwd()}")
        except:
            print("⚠️  Could not change to /var/www/plot-palette")
    
    # Run setup steps
    create_env_file()
    install_packages()
    fix_permissions()
    
    print("\n" + "=" * 50)
    print("✅ Setup complete!")
    print("\n📋 Next steps:")
    print("1. Edit story_generation/.env with your actual ANTHROPIC_API_KEY")
    print("2. Restart the Plot & Palette service: sudo systemctl restart plot-palette.service")
    print("3. Test story generation through the web interface")

if __name__ == "__main__":
    main() 