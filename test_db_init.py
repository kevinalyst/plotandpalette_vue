#!/usr/bin/env python3
"""
Test script for database initialization
Usage: python3 test_db_init.py
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

def test_database_initialization():
    """Test database initialization independently"""
    try:
        from database import db
        
        print("🔍 Testing database initialization...")
        print(f"Database: {os.environ['DB_NAME']}")
        print(f"Host: {os.environ['DB_HOST']}:{os.environ['DB_PORT']}")
        print("-" * 50)
        
        # Test database initialization
        print("Initializing database...")
        db.init_database()
        
        print("✅ Database initialization completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

def show_tables():
    """Show existing tables in the database"""
    try:
        from database import db
        
        print("\n📋 Checking existing tables...")
        with db.get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            if tables:
                print("Existing tables:")
                for i, (table_name,) in enumerate(tables, 1):
                    print(f"  {i}. {table_name}")
            else:
                print("No tables found in database")
                
            cursor.close()
            
    except Exception as e:
        print(f"❌ Error checking tables: {e}")

if __name__ == "__main__":
    print("🚀 Database Initialization Test")
    print("=" * 50)
    
    # Show existing tables first
    show_tables()
    
    # Test initialization
    success = test_database_initialization()
    
    # Show tables after initialization
    show_tables()
    
    if success:
        print("\n🎉 Database initialization test passed!")
    else:
        print("\n❌ Database initialization test failed!")
    
    sys.exit(0 if success else 1) 