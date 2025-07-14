#!/usr/bin/env python3
"""
Setup script to create .env file with Claude API key
"""

import os

def setup_env():
    api_key = "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"
    
    env_content = f"""# Claude API Configuration
CLAUDE_API_KEY={api_key}
"""
    
    # Write to .env file
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Created .env file with Claude API key")

if __name__ == "__main__":
    setup_env() 