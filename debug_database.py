#!/usr/bin/env python3
"""
Debug script to check MySQL server connection and available databases
Usage: python3 debug_database.py
"""

import mysql.connector
from mysql.connector import Error
import sys

def debug_database_connection():
    """Debug database connection and list available databases"""
    
    # Connection config (without specifying database)
    config = {
        'host': '34.142.53.204',
        'user': 'root',
        'password': 'Lihanwen1997',
        'port': 3306,
        'charset': 'utf8mb4',
        'connection_timeout': 10
    }
    
    try:
        print("🔍 Connecting to MySQL server...")
        print(f"Host: {config['host']}")
        print(f"User: {config['user']}")
        print(f"Port: {config['port']}")
        print("-" * 50)
        
        # Connect without specifying database
        connection = mysql.connector.connect(**config)
        
        if connection.is_connected():
            print("✅ Successfully connected to MySQL server!")
            
            cursor = connection.cursor()
            
            # Get server info
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print(f"📊 MySQL Server Version: {version[0]}")
            
            # List all databases
            print("\n📋 Available databases:")
            cursor.execute("SHOW DATABASES")
            databases = cursor.fetchall()
            
            for i, (db_name,) in enumerate(databases, 1):
                print(f"  {i}. {db_name}")
            
            # Check if our target database exists
            target_db = 'plotpalette-mydb'
            db_exists = any(db[0] == target_db for db in databases)
            
            print(f"\n🎯 Target database '{target_db}': {'✅ EXISTS' if db_exists else '❌ NOT FOUND'}")
            
            if not db_exists:
                print(f"\n💡 Suggestions:")
                print(f"   1. Create the database: CREATE DATABASE `{target_db}`;")
                print(f"   2. Or use an existing database from the list above")
                
                # Try to create the database
                create_db = input(f"\n❓ Would you like to create the database '{target_db}'? (y/n): ")
                if create_db.lower() == 'y':
                    try:
                        cursor.execute(f"CREATE DATABASE `{target_db}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
                        print(f"✅ Database '{target_db}' created successfully!")
                        
                        # Verify creation
                        cursor.execute("SHOW DATABASES")
                        databases = cursor.fetchall()
                        db_exists = any(db[0] == target_db for db in databases)
                        print(f"✅ Verification: Database '{target_db}' now exists: {db_exists}")
                        
                    except Error as e:
                        print(f"❌ Error creating database: {e}")
            
            cursor.close()
            connection.close()
            
            return db_exists or (create_db.lower() == 'y' if 'create_db' in locals() else False)
            
    except Error as e:
        print(f"❌ Database connection error: {e}")
        print("\n🔧 Troubleshooting tips:")
        print("   1. Check if the IP address is correct")
        print("   2. Verify the username and password")
        print("   3. Ensure the MySQL server is running")
        print("   4. Check firewall settings")
        return False
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 MySQL Database Debug Tool")
    print("=" * 50)
    
    success = debug_database_connection()
    
    if success:
        print("\n🎉 Database setup completed successfully!")
        print("You can now run your deployment script again.")
    else:
        print("\n❌ Database setup failed. Please check the connection details.")
    
    sys.exit(0 if success else 1) 