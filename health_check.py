#!/usr/bin/env python3
"""
Comprehensive Health Check for Plot & Palette Website
Tests database connection, API endpoints, recommendation service, and story generation
"""

import requests
import json
import sys
import os
import mysql.connector
from datetime import datetime
import subprocess
import time

class HealthChecker:
    def __init__(self):
        self.base_url = "http://34.39.28.3:8080"  # Your production server
        self.results = []
        
    def log_result(self, test_name, status, message, details=None):
        """Log test results"""
        result = {
            "test": test_name,
            "status": status,  # "PASS", "FAIL", "WARN"
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "details": details
        }
        self.results.append(result)
        
        # Color coding for terminal output
        color = "\033[92m" if status == "PASS" else "\033[91m" if status == "FAIL" else "\033[93m"
        reset = "\033[0m"
        print(f"{color}[{status}]{reset} {test_name}: {message}")
        if details:
            print(f"    Details: {details}")
    
    def test_database_connection(self):
        """Test MySQL database connection"""
        try:
            # Test database connection using the same logic as server.py
            import sys
            sys.path.append('/var/www/plot-palette')
            from database import get_db_connection, health_check
            
            # Test connection
            conn = get_db_connection()
            if conn:
                conn.close()
                self.log_result("Database Connection", "PASS", "Successfully connected to MySQL database")
                
                # Test health check endpoint
                is_healthy = health_check()
                if is_healthy:
                    self.log_result("Database Health Check", "PASS", "Database health check passed")
                else:
                    self.log_result("Database Health Check", "FAIL", "Database health check failed")
            else:
                self.log_result("Database Connection", "FAIL", "Failed to connect to MySQL database")
                
        except Exception as e:
            self.log_result("Database Connection", "FAIL", f"Database connection error: {str(e)}")
    
    def test_web_server_status(self):
        """Test if web server is responding"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=10)
            if response.status_code == 200:
                self.log_result("Web Server", "PASS", "Web server is responding")
            else:
                self.log_result("Web Server", "FAIL", f"Web server returned status {response.status_code}")
        except requests.exceptions.RequestException as e:
            self.log_result("Web Server", "FAIL", f"Cannot reach web server: {str(e)}")
    
    def test_health_endpoint(self):
        """Test the health endpoint"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_result("Health Endpoint", "PASS", "Health endpoint is working", data)
            else:
                self.log_result("Health Endpoint", "FAIL", f"Health endpoint returned status {response.status_code}")
        except Exception as e:
            self.log_result("Health Endpoint", "FAIL", f"Health endpoint error: {str(e)}")
    
    def test_emotion_prediction(self):
        """Test emotion prediction API"""
        try:
            # Test with sample color data
            test_data = {
                "colors": [
                    {"hex": "#FF6B6B", "percentage": 30},
                    {"hex": "#4ECDC4", "percentage": 25},
                    {"hex": "#45B7D1", "percentage": 20},
                    {"hex": "#96CEB4", "percentage": 15},
                    {"hex": "#FFEAA7", "percentage": 10}
                ]
            }
            
            response = requests.post(f"{self.base_url}/predict_emotion", 
                                   json=test_data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if 'emotions' in result:
                    self.log_result("Emotion Prediction", "PASS", 
                                  "Emotion prediction is working", 
                                  f"Top emotion: {result.get('top_emotion', 'N/A')}")
                else:
                    self.log_result("Emotion Prediction", "FAIL", 
                                  "Emotion prediction returned invalid response", result)
            else:
                self.log_result("Emotion Prediction", "FAIL", 
                              f"Emotion prediction returned status {response.status_code}")
        except Exception as e:
            self.log_result("Emotion Prediction", "FAIL", f"Emotion prediction error: {str(e)}")
    
    def test_recommendation_service(self):
        """Test painting recommendation service"""
        try:
            # Test with sample emotion data
            test_data = {
                "emotion": "happiness",
                "session_id": "health_check_session"
            }
            
            response = requests.post(f"{self.base_url}/recommend_paintings", 
                                   json=test_data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if 'paintings' in result and len(result['paintings']) > 0:
                    self.log_result("Recommendation Service", "PASS", 
                                  "Recommendation service is working", 
                                  f"Found {len(result['paintings'])} paintings")
                    
                    # Check for invalid URLs in recommendations
                    invalid_urls = []
                    for painting in result['paintings'][:3]:  # Check first 3
                        if 'image_url' in painting:
                            url = painting['image_url']
                            if not url.startswith(('http://', 'https://')):
                                invalid_urls.append(url)
                    
                    if invalid_urls:
                        self.log_result("Recommendation URLs", "WARN", 
                                      "Found invalid URLs in recommendations", 
                                      invalid_urls)
                    else:
                        self.log_result("Recommendation URLs", "PASS", "All recommendation URLs are valid")
                        
                else:
                    self.log_result("Recommendation Service", "FAIL", 
                                  "Recommendation service returned no paintings")
            else:
                self.log_result("Recommendation Service", "FAIL", 
                              f"Recommendation service returned status {response.status_code}")
        except Exception as e:
            self.log_result("Recommendation Service", "FAIL", f"Recommendation service error: {str(e)}")
    
    def test_story_generation(self):
        """Test story generation service"""
        try:
            # Test with minimal data
            test_data = {
                "user_name": "HealthCheck",
                "emotion": "happiness",
                "emotion_confidence": 0.8,
                "narrative_style": "fantasy",
                "paintings": ["Test Painting 1", "Test Painting 2", "Test Painting 3"],
                "session_id": "health_check_session"
            }
            
            response = requests.post(f"{self.base_url}/generate_story", 
                                   json=test_data, timeout=60)  # Longer timeout for AI
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success') and result.get('story'):
                    self.log_result("Story Generation", "PASS", 
                                  "Story generation is working", 
                                  f"Story length: {len(result['story'])} characters")
                else:
                    self.log_result("Story Generation", "FAIL", 
                                  "Story generation failed", result.get('error', 'Unknown error'))
            else:
                self.log_result("Story Generation", "FAIL", 
                              f"Story generation returned status {response.status_code}")
        except Exception as e:
            self.log_result("Story Generation", "FAIL", f"Story generation error: {str(e)}")
    
    def test_systemd_service(self):
        """Test systemd service status"""
        try:
            result = subprocess.run(['sudo', 'systemctl', 'is-active', 'plot-palette.service'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0 and result.stdout.strip() == 'active':
                self.log_result("Systemd Service", "PASS", "plot-palette.service is active")
                
                # Check if there are recent errors
                log_result = subprocess.run(['sudo', 'journalctl', '-u', 'plot-palette.service', 
                                           '--since', '1 hour ago', '--grep=ERROR'], 
                                          capture_output=True, text=True)
                
                if log_result.stdout:
                    self.log_result("Service Errors", "WARN", 
                                  "Found recent errors in service logs", 
                                  "Check with: sudo journalctl -u plot-palette.service")
                else:
                    self.log_result("Service Errors", "PASS", "No recent errors in service logs")
                    
            else:
                self.log_result("Systemd Service", "FAIL", "plot-palette.service is not active")
        except Exception as e:
            self.log_result("Systemd Service", "FAIL", f"Cannot check systemd service: {str(e)}")
    
    def test_file_permissions(self):
        """Test critical file permissions"""
        critical_paths = [
            "/var/www/plot-palette",
            "/var/www/plot-palette/uploads",
            "/var/www/plot-palette/venv",
            "/var/www/plot-palette/.env"
        ]
        
        for path in critical_paths:
            try:
                if os.path.exists(path):
                    stat = os.stat(path)
                    if os.access(path, os.R_OK):
                        self.log_result("File Permissions", "PASS", f"{path} is accessible")
                    else:
                        self.log_result("File Permissions", "FAIL", f"{path} is not accessible")
                else:
                    self.log_result("File Permissions", "WARN", f"{path} does not exist")
            except Exception as e:
                self.log_result("File Permissions", "FAIL", f"Cannot check {path}: {str(e)}")
    
    def generate_report(self):
        """Generate a summary report"""
        print("\n" + "="*60)
        print("HEALTH CHECK SUMMARY")
        print("="*60)
        
        total_tests = len(self.results)
        passed = len([r for r in self.results if r['status'] == 'PASS'])
        failed = len([r for r in self.results if r['status'] == 'FAIL'])
        warnings = len([r for r in self.results if r['status'] == 'WARN'])
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed}")
        print(f"⚠️  Warnings: {warnings}")
        print(f"❌ Failed: {failed}")
        
        if failed > 0:
            print("\n🚨 CRITICAL ISSUES:")
            for result in self.results:
                if result['status'] == 'FAIL':
                    print(f"  - {result['test']}: {result['message']}")
        
        if warnings > 0:
            print("\n⚠️  WARNINGS:")
            for result in self.results:
                if result['status'] == 'WARN':
                    print(f"  - {result['test']}: {result['message']}")
        
        # Save detailed report
        report_file = f"health_check_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_file}")
        
        return failed == 0
    
    def run_all_tests(self):
        """Run all health checks"""
        print("🏥 Starting comprehensive health check...")
        print(f"🌐 Target: {self.base_url}")
        print(f"⏰ Time: {datetime.now().isoformat()}")
        print("="*60)
        
        # Run tests in logical order
        self.test_systemd_service()
        self.test_file_permissions()
        self.test_web_server_status()
        self.test_health_endpoint()
        self.test_database_connection()
        self.test_emotion_prediction()
        self.test_recommendation_service()
        self.test_story_generation()
        
        return self.generate_report()

if __name__ == "__main__":
    checker = HealthChecker()
    success = checker.run_all_tests()
    sys.exit(0 if success else 1) 