#!/usr/bin/env python3
"""
Guardian Eye Production Readiness Test
Comprehensive testing for deployment readiness
"""

import requests
import json
import time
from datetime import datetime
import sys

class ProductionReadinessTest:
    def __init__(self):
        # URLs
        self.mobile_app_url = "https://device-security-hub-2.preview.emergentagent.com"
        self.dashboard_url = "https://device-security-hub-2.preview.emergentagent.com/dashboard.html"
        self.backend_api_url = "https://device-security-hub-2.preview.emergentagent.com/api"
        
        # Test credentials
        self.test_email = "test@guardianeye.com"
        self.test_password = "test123456"
        
        # Firebase config
        self.firebase_config = {
            "apiKey": "AIzaSyDCc8qBTWxO-sX5dhlC6mDWokomgScIFwQ",
            "authDomain": "guardianeye-feb2d.firebaseapp.com",
            "databaseURL": "https://guardianeye-feb2d-default-rtdb.firebaseio.com",
            "projectId": "guardianeye-feb2d",
            "storageBucket": "guardianeye-feb2d.firebasestorage.app"
        }
        
        self.test_results = []
        
    def log_test(self, test_name, status, details=""):
        """Log test results"""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} {test_name}: {status}")
        if details:
            print(f"   Details: {details}")
        print()

    def test_backend_api_health(self):
        """Test backend API health and endpoints"""
        try:
            # Test root endpoint
            response = requests.get(f"{self.backend_api_url}/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("message") == "Hello World":
                    self.log_test("Backend API Health", "PASS", "Root endpoint responding correctly")
                else:
                    self.log_test("Backend API Health", "FAIL", f"Unexpected response: {data}")
                    return False
            else:
                self.log_test("Backend API Health", "FAIL", f"Status: {response.status_code}")
                return False
                
            # Test status endpoints
            status_response = requests.get(f"{self.backend_api_url}/status", timeout=10)
            if status_response.status_code == 200:
                self.log_test("Backend Status Endpoint", "PASS", "Status endpoint accessible")
            else:
                self.log_test("Backend Status Endpoint", "FAIL", f"Status: {status_response.status_code}")
                return False
                
            # Test POST to status
            post_data = {"client_name": "production_test"}
            post_response = requests.post(f"{self.backend_api_url}/status", json=post_data, timeout=10)
            if post_response.status_code == 200:
                post_result = post_response.json()
                if "id" in post_result and "timestamp" in post_result:
                    self.log_test("Backend POST Operation", "PASS", f"Created record with ID: {post_result['id'][:8]}...")
                else:
                    self.log_test("Backend POST Operation", "FAIL", "Missing required fields in response")
                    return False
            else:
                self.log_test("Backend POST Operation", "FAIL", f"Status: {post_response.status_code}")
                return False
                
            return True
            
        except Exception as e:
            self.log_test("Backend API Health", "FAIL", f"Error: {str(e)}")
            return False

    def test_firebase_authentication(self):
        """Test Firebase authentication system"""
        try:
            auth_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={self.firebase_config['apiKey']}"
            
            payload = {
                "email": self.test_email,
                "password": self.test_password,
                "returnSecureToken": True
            }
            
            response = requests.post(auth_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'idToken' in data and 'localId' in data:
                    self.log_test("Firebase Authentication", "PASS", f"User authenticated: {data['localId'][:10]}...")
                    return data
                else:
                    self.log_test("Firebase Authentication", "FAIL", "Missing authentication tokens")
                    return None
            else:
                error_data = response.json() if response.content else {}
                error_msg = error_data.get('error', {}).get('message', 'Unknown error')
                self.log_test("Firebase Authentication", "FAIL", f"Error: {error_msg}")
                return None
                
        except Exception as e:
            self.log_test("Firebase Authentication", "FAIL", f"Error: {str(e)}")
            return None

    def test_firebase_database_operations(self, auth_data):
        """Test Firebase database operations"""
        if not auth_data:
            self.log_test("Firebase Database Operations", "SKIP", "No auth data available")
            return False
            
        try:
            # Test read operation
            db_url = f"{self.firebase_config['databaseURL']}/devices.json"
            params = {"auth": auth_data['idToken']}
            
            response = requests.get(db_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                device_count = len(data) if data else 0
                self.log_test("Firebase Database Read", "PASS", f"Found {device_count} devices")
                
                # Test write operation
                test_device_id = f"prod_test_{int(time.time())}"
                test_device_data = {
                    "deviceName": "Production Test Device",
                    "status": "NORMAL",
                    "lastSeen": int(time.time() * 1000),
                    "testDevice": True
                }
                
                write_url = f"{self.firebase_config['databaseURL']}/devices/{test_device_id}.json"
                write_response = requests.put(write_url, json=test_device_data, params=params, timeout=10)
                
                if write_response.status_code == 200:
                    self.log_test("Firebase Database Write", "PASS", f"Test device created: {test_device_id}")
                    
                    # Test update operation
                    update_data = {"status": "STOLEN", "markedStolenAt": int(time.time() * 1000)}
                    update_response = requests.patch(write_url, json=update_data, params=params, timeout=10)
                    
                    if update_response.status_code == 200:
                        self.log_test("Firebase Database Update", "PASS", "Device status updated successfully")
                        
                        # Cleanup - delete test device
                        delete_response = requests.delete(write_url, params=params, timeout=10)
                        if delete_response.status_code == 200:
                            self.log_test("Firebase Database Cleanup", "PASS", "Test device cleaned up")
                        
                        return True
                    else:
                        self.log_test("Firebase Database Update", "FAIL", f"Update failed: {update_response.status_code}")
                        return False
                else:
                    self.log_test("Firebase Database Write", "FAIL", f"Write failed: {write_response.status_code}")
                    return False
            else:
                self.log_test("Firebase Database Read", "FAIL", f"Read failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Firebase Database Operations", "FAIL", f"Error: {str(e)}")
            return False

    def test_web_interfaces(self):
        """Test web interface accessibility"""
        try:
            # Test mobile app
            mobile_response = requests.get(self.mobile_app_url, timeout=10)
            if mobile_response.status_code == 200:
                self.log_test("Mobile App Interface", "PASS", "Mobile app accessible")
            else:
                self.log_test("Mobile App Interface", "FAIL", f"Status: {mobile_response.status_code}")
                return False
                
            # Test dashboard
            dashboard_response = requests.get(self.dashboard_url, timeout=10)
            if dashboard_response.status_code == 200:
                content = dashboard_response.text
                
                # Check for essential elements
                essential_elements = [
                    "Guardian Eye Dashboard",
                    "firebase",
                    "Mark as Stolen",
                    "Device Location",
                    "Captured Photos"
                ]
                
                missing_elements = [elem for elem in essential_elements if elem not in content]
                
                if not missing_elements:
                    self.log_test("Web Dashboard Interface", "PASS", "All essential elements present")
                    return True
                else:
                    self.log_test("Web Dashboard Interface", "FAIL", f"Missing elements: {missing_elements}")
                    return False
            else:
                self.log_test("Web Dashboard Interface", "FAIL", f"Status: {dashboard_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Web Interfaces", "FAIL", f"Error: {str(e)}")
            return False

    def test_service_files_integrity(self):
        """Test that all required service files exist"""
        try:
            import os
            
            required_files = [
                "/app/frontend/services/firebase.ts",
                "/app/frontend/services/DeviceMonitor.ts",
                "/app/frontend/services/LocationService.ts",
                "/app/frontend/services/CameraService.ts",
                "/app/frontend/services/DataWipeService.ts",
                "/app/frontend/services/EncryptionService.ts",
                "/app/frontend/services/NotificationService.ts",
                "/app/frontend/contexts/AuthContext.tsx",
                "/app/frontend/public/dashboard.html"
            ]
            
            missing_files = [f for f in required_files if not os.path.exists(f)]
            
            if not missing_files:
                self.log_test("Service Files Integrity", "PASS", f"All {len(required_files)} required files present")
                return True
            else:
                self.log_test("Service Files Integrity", "FAIL", f"Missing files: {missing_files}")
                return False
                
        except Exception as e:
            self.log_test("Service Files Integrity", "FAIL", f"Error: {str(e)}")
            return False

    def run_production_tests(self):
        """Run all production readiness tests"""
        print("🚀 Starting Guardian Eye Production Readiness Testing")
        print("=" * 70)
        print()
        
        # Test 1: Service files integrity
        self.test_service_files_integrity()
        
        # Test 2: Backend API health
        backend_healthy = self.test_backend_api_health()
        
        # Test 3: Web interfaces
        interfaces_working = self.test_web_interfaces()
        
        # Test 4: Firebase authentication
        auth_data = self.test_firebase_authentication()
        
        # Test 5: Firebase database operations
        if auth_data:
            database_working = self.test_firebase_database_operations(auth_data)
        else:
            database_working = False
        
        # Summary
        print("=" * 70)
        print("📊 PRODUCTION READINESS SUMMARY")
        print("=" * 70)
        
        passed = len([r for r in self.test_results if r['status'] == 'PASS'])
        failed = len([r for r in self.test_results if r['status'] == 'FAIL'])
        skipped = len([r for r in self.test_results if r['status'] in ['SKIP', 'INFO']])
        total = len(self.test_results)
        
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️  Skipped/Info: {skipped}")
        print(f"📋 Total: {total}")
        print()
        
        if failed > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if result['status'] == 'FAIL':
                    print(f"   • {result['test']}: {result['details']}")
            print()
        
        success_rate = (passed / (passed + failed)) * 100 if (passed + failed) > 0 else 0
        print(f"🎯 Success Rate: {success_rate:.1f}%")
        
        # Production readiness assessment
        critical_systems = [backend_healthy, interfaces_working, auth_data is not None, database_working]
        production_ready = all(critical_systems) and success_rate >= 90
        
        if production_ready:
            print("\n🎉 PRODUCTION READY!")
            print("✅ All critical systems operational")
            print("✅ Guardian Eye is ready for deployment")
        else:
            print("\n⚠️  NOT PRODUCTION READY")
            print("❌ Critical issues need to be resolved before deployment")
        
        return production_ready

if __name__ == "__main__":
    tester = ProductionReadinessTest()
    success = tester.run_production_tests()
    
    if success:
        print("\n🚀 Guardian Eye passed production readiness testing!")
        sys.exit(0)
    else:
        print("\n⚠️  Guardian Eye requires fixes before production deployment.")
        sys.exit(1)