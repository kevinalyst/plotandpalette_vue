#!/usr/bin/env python3
"""
Plot & Palette Application Diagnostic Script
===========================================

This script performs comprehensive health checks on the Plot & Palette application
and attempts to automatically repair common issues.

Philosophy: Check, Report, and Attempt to Repair

Usage: python3 diagnostic.py
"""

import subprocess
import requests
import time
import sys
import os
import re
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# Configuration
SERVICES = {
    'nginx': {'port': 80, 'health_path': '/health'},
    'backend': {'port': 5003, 'health_path': '/health'},
    'emotion-api': {'port': 5001, 'health_path': '/health'},
    'story-api': {'port': 5002, 'health_path': '/health'},
    'db': {'port': 3306, 'health_path': None}  # DB checked indirectly
}

DOCKER_COMPOSE_FILE = 'docker-compose.yml'
WAIT_TIME_AFTER_RESTART = 15  # seconds

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

class DiagnosticResults:
    """Track diagnostic results across all checks"""
    def __init__(self):
        self.results: Dict[str, str] = {}
        self.repairs_attempted: List[str] = []
        self.repairs_successful: List[str] = []
        
    def add_result(self, check_name: str, status: str):
        self.results[check_name] = status
        
    def add_repair(self, repair: str, successful: bool = False):
        self.repairs_attempted.append(repair)
        if successful:
            self.repairs_successful.append(repair)

def print_header(title: str):
    """Print a formatted section header"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{title.center(60)}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.END}")

def print_status(check_name: str, status: str, details: str = ""):
    """Print a formatted status line"""
    status_color = Colors.GREEN if status == "PASS" else Colors.RED if status == "FAIL" else Colors.YELLOW
    print(f"{check_name:<30} [{status_color}{status}{Colors.END}] {details}")

def run_command(command: str, timeout: int = 30) -> Tuple[bool, str, str]:
    """
    Execute a shell command and return (success, stdout, stderr)
    """
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=timeout
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", f"Command timed out after {timeout} seconds"
    except Exception as e:
        return False, "", str(e)

def check_docker_health(results: DiagnosticResults) -> bool:
    """
    Check the health status of all Docker containers
    """
    print_header("DOCKER CONTAINER HEALTH CHECK")
    
    # Get container status
    success, stdout, stderr = run_command("docker-compose ps")
    
    if not success:
        print_status("Docker Compose", "FAIL", f"Error: {stderr}")
        results.add_result("Docker Compose", "FAIL")
        return False
    
    lines = stdout.strip().split('\n')
    unhealthy_services = []
    healthy_services = []
    
    # Parse docker-compose ps output
    for line in lines[1:]:  # Skip header
        if line.strip() and not line.startswith('WARN'):
            # Extract service name and status
            parts = line.split()
            if len(parts) >= 5:
                container_name = parts[0]
                status_info = ' '.join(parts[4:])
                
                # Extract service name from container name
                service_name = container_name.replace('plot-palette-', '').replace('plot-palette', 'backend')
                
                if 'unhealthy' in status_info.lower():
                    unhealthy_services.append(service_name)
                    print_status(f"Container: {service_name}", "FAIL", "unhealthy")
                elif 'healthy' in status_info.lower() or 'up' in status_info.lower():
                    healthy_services.append(service_name)
                    print_status(f"Container: {service_name}", "PASS", "healthy")
                else:
                    print_status(f"Container: {service_name}", "WARN", status_info)
    
    # Attempt repairs for unhealthy services
    all_healthy = True
    for service in unhealthy_services:
        all_healthy = False
        print(f"\n{Colors.YELLOW}Attempting to repair unhealthy service: {service}{Colors.END}")
        
        # Get logs first
        print(f"Getting logs for {service}...")
        log_success, log_output, _ = run_command(f"docker-compose logs --tail=10 {service}")
        if log_success and log_output.strip():
            print(f"Recent logs:\n{log_output}")
        
        # Attempt restart
        print(f"Restarting {service}...")
        restart_success, _, restart_error = run_command(f"docker-compose restart {service}")
        results.add_repair(f"Restart {service}", restart_success)
        
        if restart_success:
            print(f"Waiting {WAIT_TIME_AFTER_RESTART} seconds for {service} to stabilize...")
            time.sleep(WAIT_TIME_AFTER_RESTART)
            
            # Check if restart was successful
            success, stdout, _ = run_command("docker-compose ps")
            if success and 'unhealthy' not in stdout:
                print_status(f"Repair: {service}", "PASS", "restart successful")
                results.repairs_successful.append(f"Restart {service}")
                all_healthy = True
            else:
                print_status(f"Repair: {service}", "FAIL", "still unhealthy after restart")
        else:
            print_status(f"Repair: {service}", "FAIL", f"restart failed: {restart_error}")
    
    results.add_result("Docker Health", "PASS" if all_healthy else "FAIL")
    return all_healthy

def check_nginx_endpoint(results: DiagnosticResults) -> bool:
    """
    Check if Nginx public endpoint is accessible
    """
    print_header("NGINX PUBLIC ENDPOINT CHECK")
    
    try:
        response = requests.get("http://localhost:80", timeout=10)
        if response.status_code == 200:
            print_status("Nginx Endpoint", "PASS", f"HTTP {response.status_code}")
            results.add_result("Nginx Endpoint", "PASS")
            return True
        else:
            print_status("Nginx Endpoint", "FAIL", f"HTTP {response.status_code}")
            
            # Attempt repair
            print(f"\n{Colors.YELLOW}Attempting to repair Nginx...{Colors.END}")
            restart_success, _, restart_error = run_command("docker-compose restart nginx")
            results.add_repair("Restart nginx", restart_success)
            
            if restart_success:
                time.sleep(10)
                # Re-test
                try:
                    response = requests.get("http://localhost:80", timeout=10)
                    if response.status_code == 200:
                        print_status("Repair: Nginx", "PASS", "restart successful")
                        results.repairs_successful.append("Restart nginx")
                        results.add_result("Nginx Endpoint", "PASS")
                        return True
                    else:
                        print_status("Repair: Nginx", "FAIL", f"still returning HTTP {response.status_code}")
                except requests.RequestException as e:
                    print_status("Repair: Nginx", "FAIL", f"still not accessible: {str(e)}")
            else:
                print_status("Repair: Nginx", "FAIL", f"restart failed: {restart_error}")
            
            results.add_result("Nginx Endpoint", "FAIL")
            return False
            
    except requests.RequestException as e:
        print_status("Nginx Endpoint", "FAIL", f"Connection error: {str(e)}")
        results.add_result("Nginx Endpoint", "FAIL")
        return False

def check_backend_api(results: DiagnosticResults) -> bool:
    """
    Check backend API health endpoint
    """
    print_header("BACKEND API CHECK")
    
    try:
        response = requests.get("http://localhost:5003/health", timeout=10)
        if response.status_code == 200:
            print_status("Backend API", "PASS", f"HTTP {response.status_code}")
            results.add_result("Backend API", "PASS")
            return True
        else:
            print_status("Backend API", "FAIL", f"HTTP {response.status_code}")
            return attempt_api_repair("backend", results)
            
    except requests.RequestException as e:
        print_status("Backend API", "FAIL", f"Connection error: {str(e)}")
        return attempt_api_repair("backend", results)

def check_microservices(results: DiagnosticResults) -> bool:
    """
    Check emotion and story API health endpoints
    """
    print_header("MICROSERVICES API CHECK")
    
    all_healthy = True
    
    # Check Emotion API
    try:
        response = requests.get("http://localhost:5001/health", timeout=10)
        if response.status_code == 200:
            print_status("Emotion API", "PASS", f"HTTP {response.status_code}")
            results.add_result("Emotion API", "PASS")
        else:
            print_status("Emotion API", "FAIL", f"HTTP {response.status_code}")
            all_healthy = False
            attempt_api_repair("emotion-api", results)
    except requests.RequestException as e:
        print_status("Emotion API", "FAIL", f"Connection error: {str(e)}")
        all_healthy = False
        attempt_api_repair("emotion-api", results)
    
    # Check Story API
    try:
        response = requests.get("http://localhost:5002/health", timeout=10)
        if response.status_code == 200:
            print_status("Story API", "PASS", f"HTTP {response.status_code}")
            results.add_result("Story API", "PASS")
        else:
            print_status("Story API", "FAIL", f"HTTP {response.status_code}")
            all_healthy = False
            attempt_api_repair("story-api", results)
    except requests.RequestException as e:
        print_status("Story API", "FAIL", f"Connection error: {str(e)}")
        all_healthy = False
        attempt_api_repair("story-api", results)
    
    return all_healthy

def attempt_api_repair(service_name: str, results: DiagnosticResults) -> bool:
    """
    Attempt to repair a failed API service
    """
    print(f"\n{Colors.YELLOW}Attempting to repair {service_name}...{Colors.END}")
    
    # Get logs first
    print(f"Getting logs for {service_name}...")
    log_success, log_output, _ = run_command(f"docker-compose logs --tail=10 {service_name}")
    if log_success and log_output.strip():
        print(f"Recent logs:\n{log_output}")
    
    # Attempt restart
    restart_success, _, restart_error = run_command(f"docker-compose restart {service_name}")
    results.add_repair(f"Restart {service_name}", restart_success)
    
    if restart_success:
        time.sleep(10)
        
        # Re-test the API
        port_map = {"backend": 5003, "emotion-api": 5001, "story-api": 5002}
        port = port_map.get(service_name, 5000)
        
        try:
            health_path = "/health"  # All services now use /health
            response = requests.get(f"http://localhost:{port}{health_path}", timeout=10)
            if response.status_code == 200:
                print_status(f"Repair: {service_name}", "PASS", "restart successful")
                results.repairs_successful.append(f"Restart {service_name}")
                results.add_result(f"{service_name.title()} API", "PASS")
                return True
            else:
                print_status(f"Repair: {service_name}", "FAIL", f"still returning HTTP {response.status_code}")
        except requests.RequestException as e:
            print_status(f"Repair: {service_name}", "FAIL", f"still not accessible: {str(e)}")
    else:
        print_status(f"Repair: {service_name}", "FAIL", f"restart failed: {restart_error}")
    
    results.add_result(f"{service_name.title()} API", "FAIL")
    return False

def check_database_connection(results: DiagnosticResults) -> bool:
    """
    Check database connection (indirectly through backend API)
    """
    print_header("DATABASE CONNECTION CHECK")
    
    # Database health is checked indirectly through backend API
    backend_status = results.results.get("Backend API", "UNKNOWN")
    
    if backend_status == "PASS":
        print_status("Database Connection", "PASS", "backend API responding (implies DB is healthy)")
        results.add_result("Database Connection", "PASS")
        return True
    else:
        print_status("Database Connection", "FAIL", "backend API not responding")
        
        # Attempt database repair
        print(f"\n{Colors.YELLOW}Attempting to repair database connection...{Colors.END}")
        
        # Check if it's a DB-specific issue
        log_success, log_output, _ = run_command("docker-compose logs --tail=20 backend")
        if log_success and any(keyword in log_output.lower() for keyword in ['database', 'mysql', 'connection']):
            print("Database connection error detected in backend logs")
            print("Restarting both backend and database...")
            
            restart_success, _, restart_error = run_command("docker-compose restart backend db")
            results.add_repair("Restart backend and db", restart_success)
            
            if restart_success:
                time.sleep(WAIT_TIME_AFTER_RESTART)
                # Re-test through backend
                try:
                    response = requests.get("http://localhost:5003/health", timeout=10)
                    if response.status_code == 200:
                        print_status("Repair: Database", "PASS", "restart successful")
                        results.repairs_successful.append("Restart backend and db")
                        results.add_result("Database Connection", "PASS")
                        return True
                except requests.RequestException:
                    pass
            
            print_status("Repair: Database", "FAIL", "restart did not resolve the issue")
        else:
            print_status("Database Connection", "WARN", "no clear database errors in logs")
        
        results.add_result("Database Connection", "FAIL")
        return False

def check_configuration(results: DiagnosticResults) -> bool:
    """
    Check for minor configuration issues
    """
    print_header("CONFIGURATION CHECK")
    
    all_good = True
    
    # Check docker-compose.yml for obsolete version attribute
    if os.path.exists(DOCKER_COMPOSE_FILE):
        try:
            with open(DOCKER_COMPOSE_FILE, 'r') as f:
                content = f.read()
                if content.strip().startswith('version:'):
                    print_status("Docker Compose Version", "WARN", 
                               "The 'version' attribute is obsolete and should be removed")
                    all_good = False
                else:
                    print_status("Docker Compose Version", "PASS", "no obsolete version attribute")
        except Exception as e:
            print_status("Docker Compose Config", "FAIL", f"Error reading file: {str(e)}")
            all_good = False
    else:
        print_status("Docker Compose Config", "FAIL", f"{DOCKER_COMPOSE_FILE} not found")
        all_good = False
    
    # Check if script is being run from correct directory
    if os.path.exists(DOCKER_COMPOSE_FILE) and os.path.exists('server.py'):
        print_status("Working Directory", "PASS", "running from correct project directory")
    else:
        print_status("Working Directory", "WARN", "may not be running from project root")
        all_good = False
    
    results.add_result("Configuration", "PASS" if all_good else "WARN")
    return all_good

def print_final_summary(results: DiagnosticResults):
    """
    Print a comprehensive summary of all diagnostic results
    """
    print_header("DIAGNOSTIC SUMMARY")
    
    # Print all results
    passed = 0
    failed = 0
    warnings = 0
    
    for check, status in results.results.items():
        if status == "PASS":
            passed += 1
        elif status == "FAIL":
            failed += 1
        else:
            warnings += 1
        print_status(check, status)
    
    print(f"\n{Colors.BOLD}Overall Results:{Colors.END}")
    print(f"✅ Passed: {Colors.GREEN}{passed}{Colors.END}")
    print(f"❌ Failed: {Colors.RED}{failed}{Colors.END}")
    print(f"⚠️  Warnings: {Colors.YELLOW}{warnings}{Colors.END}")
    
    # Print repair summary
    if results.repairs_attempted:
        print(f"\n{Colors.BOLD}Repair Actions Taken:{Colors.END}")
        for repair in results.repairs_attempted:
            status = "✅ SUCCESS" if repair in results.repairs_successful else "❌ FAILED"
            print(f"  {repair}: {status}")
    
    # Overall health assessment
    print(f"\n{Colors.BOLD}System Health Assessment:{Colors.END}")
    if failed == 0:
        if warnings == 0:
            print(f"{Colors.GREEN}🎉 EXCELLENT: All systems are healthy!{Colors.END}")
        else:
            print(f"{Colors.YELLOW}✅ GOOD: Core systems healthy, minor warnings present{Colors.END}")
    elif failed <= 2 and len(results.repairs_successful) > 0:
        print(f"{Colors.YELLOW}🔧 RECOVERING: Some issues detected but repairs were successful{Colors.END}")
    else:
        print(f"{Colors.RED}🚨 CRITICAL: Multiple system failures detected{Colors.END}")
        print(f"{Colors.RED}   Manual intervention may be required{Colors.END}")

def main():
    """
    Main diagnostic function
    """
    print(f"{Colors.BOLD}{Colors.BLUE}")
    print("=" * 80)
    print("PLOT & PALETTE APPLICATION DIAGNOSTIC SCRIPT".center(80))
    print("=" * 80)
    print(f"{Colors.END}")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Philosophy: Check, Report, and Attempt to Repair")
    
    results = DiagnosticResults()
    
    try:
        # Run all diagnostic checks
        check_docker_health(results)
        check_nginx_endpoint(results)
        check_backend_api(results)
        check_microservices(results)
        check_database_connection(results)
        check_configuration(results)
        
        # Print final summary
        print_final_summary(results)
        
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Diagnostic interrupted by user{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Unexpected error during diagnostics: {str(e)}{Colors.END}")
        sys.exit(1)
    
    print(f"\nDiagnostic completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Exit with appropriate code
    failed_checks = sum(1 for status in results.results.values() if status == "FAIL")
    sys.exit(0 if failed_checks == 0 else 1)

if __name__ == "__main__":
    main() 