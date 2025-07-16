#!/usr/bin/env python3
"""
Test script for external database connectivity
Usage: python3 test_db_connection.py
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set database configuration
os.environ['DB_HOST'] = '34.142.53.204'
os.environ['DB_USER'] = 'root'
os.environ['DB_PASSWORD'] = 'Lihanwen1997'
os.environ['DB_NAME'] = 'plotpalette-mydb'
os.environ['DB_PORT'] = '3306'

def test_database_connection():
    """Test database connection and basic functionality"""
    try:
        from database import db
        print("Testing database connection...")
        
        # Test basic connection
        if db.health_check():
            print("✅ Database connection successful")
        else:
            print("❌ Database connection failed")
            return False
        
        # Test database initialization
        print("Testing database initialization...")
        db.init_database()
        print("✅ Database initialization successful")
        
        # Test basic user creation
        print("Testing basic database operations...")
        test_user = db.create_or_get_user(
            session_id="test_session_123",
            user_agent="Test User Agent",
            ip_address="127.0.0.1"
        )
        
        if test_user:
            print("✅ User creation/retrieval successful")
        else:
            print("❌ User creation/retrieval failed")
            return False
        
        print("\n🎉 All database tests passed!")
        print(f"Database: {os.environ['DB_NAME']}")
        print(f"Host: {os.environ['DB_HOST']}:{os.environ['DB_PORT']}")
        print(f"User: {os.environ['DB_USER']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_database_connection()
    sys.exit(0 if success else 1) 