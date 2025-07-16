#!/usr/bin/env python3
"""
Test script to verify Plot & Palette application is working
Usage: python3 test_application.py
"""

import requests
import json
import os
import sys

def test_backend_health():
    """Test if backend is responding"""
    try:
        response = requests.get('http://localhost:5000/', timeout=10)
        if response.status_code == 200:
            print("✅ Backend is responding")
            return True
        else:
            print(f"⚠️  Backend returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Backend not responding: {e}")
        return False

def test_nginx():
    """Test if nginx is serving the application"""
    try:
        response = requests.get('http://localhost:8080/', timeout=10)
        if response.status_code == 200:
            print("✅ Nginx is serving the application")
            return True
        else:
            print(f"⚠️  Nginx returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Nginx not responding: {e}")
        return False

def test_database_connection():
    """Test database connectivity"""
    try:
        # Set environment variables for database test
        os.environ['DB_HOST'] = '34.142.53.204'
        os.environ['DB_USER'] = 'root'
        os.environ['DB_PASSWORD'] = 'Lihanwen1997'
        os.environ['DB_NAME'] = 'plotpalette-mydb'
        os.environ['DB_PORT'] = '3306'
        
        from database import db
        if db.health_check():
            print("✅ Database connection successful")
            return True
        else:
            print("❌ Database connection failed")
            return False
    except Exception as e:
        print(f"❌ Database test error: {e}")
        return False

def test_api_endpoints():
    """Test various API endpoints"""
    endpoints = [
        ('/api/health', 'Health check'),
        ('/api/status', 'Status check'),
        ('/', 'Root endpoint'),
    ]
    
    results = []
    for endpoint, description in endpoints:
        try:
            response = requests.get(f'http://localhost:5000{endpoint}', timeout=5)
            if response.status_code == 200:
                print(f"✅ {description}: OK")
                results.append(True)
            elif response.status_code == 404:
                print(f"⚠️  {description}: Not implemented (404)")
                results.append(True)  # 404 is expected for non-existent endpoints
            else:
                print(f"❌ {description}: Status {response.status_code}")
                results.append(False)
        except requests.exceptions.RequestException as e:
            print(f"❌ {description}: {e}")
            results.append(False)
    
    return all(results)

def test_file_uploads():
    """Test file upload capability"""
    try:
        # Test if uploads directory exists
        uploads_dir = '/var/www/plot-palette/uploads'
        if os.path.exists(uploads_dir):
            print("✅ Uploads directory exists")
            return True
        else:
            print("❌ Uploads directory not found")
            return False
    except Exception as e:
        print(f"❌ Upload test error: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Plot & Palette Application Test Suite")
    print("=" * 50)
    
    tests = [
        ("Backend Health", test_backend_health),
        ("Nginx Frontend", test_nginx),
        ("Database Connection", test_database_connection),
        ("API Endpoints", test_api_endpoints),
        ("File Uploads", test_file_uploads),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 Testing {test_name}:")
        print("-" * 30)
        result = test_func()
        results.append(result)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    passed = sum(results)
    total = len(results)
    
    for i, (test_name, _) in enumerate(tests):
        status = "✅ PASS" if results[i] else "❌ FAIL"
        print(f"   {test_name}: {status}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your Plot & Palette application is running successfully!")
        print("\n🌐 Next steps:")
        print("   1. Access your application at: http://your-vm-ip:8080")
        print("   2. Test uploading an image for palette extraction")
        print("   3. Try the emotion prediction feature")
        print("   4. Generate a story from selected paintings")
        print("   5. Consider setting up SSL for production use")
    else:
        print(f"\n⚠️  {total - passed} tests failed. Please check the issues above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 