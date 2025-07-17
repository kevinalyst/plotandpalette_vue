#!/bin/bash
# Fix permissions for story generation

echo "🔧 Fixing Story Generation Permissions..."

# Get the current working directory
PROJECT_DIR="/var/www/plot-palette"
STORY_DIR="$PROJECT_DIR/story_generation"

# 1. Fix directory ownership
echo "Setting proper ownership..."
sudo chown -R www-data:www-data "$STORY_DIR"

# 2. Fix directory permissions
echo "Setting proper permissions..."
sudo chmod 755 "$STORY_DIR"
sudo chmod 644 "$STORY_DIR"/*.py 2>/dev/null || true
sudo chmod 644 "$STORY_DIR"/*.txt 2>/dev/null || true

# 3. Remove existing .env if it has wrong permissions
if [ -f "$STORY_DIR/.env" ]; then
    echo "Removing existing .env file..."
    sudo rm -f "$STORY_DIR/.env"
fi

# 4. Create .env file with proper content
echo "Creating .env file..."
sudo tee "$STORY_DIR/.env" > /dev/null << 'EOF'
# Claude API Configuration
CLAUDE_API_KEY=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
EOF

# 5. Set proper permissions on .env file
sudo chown www-data:www-data "$STORY_DIR/.env"
sudo chmod 644 "$STORY_DIR/.env"

# 6. Install required packages in virtual environment
echo "Installing required packages in virtual environment..."
cd "$PROJECT_DIR"
source venv/bin/activate
pip install anthropic python-dotenv Pillow

# 7. Test the setup
echo "Testing story generation setup..."
if [ -f "$STORY_DIR/.env" ]; then
    echo "✅ .env file created successfully"
else
    echo "❌ .env file creation failed"
fi

# Test imports
if python3 -c "import anthropic; import dotenv; import PIL; print('✅ All packages available')" 2>/dev/null; then
    echo "✅ All required packages are installed"
else
    echo "❌ Some packages are missing"
fi

# 8. Test file permissions
echo "Checking file permissions..."
ls -la "$STORY_DIR/.env"
ls -la "$STORY_DIR"/*.py

echo "✅ Story generation permissions fixed!"
echo "Now you can test with: python3 debug_story_generation.py" 