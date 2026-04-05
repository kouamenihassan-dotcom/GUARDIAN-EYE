#!/usr/bin/env python3
"""
Guardian Eye Phase 2 Testing - GPS Tracking & Camera Capture
Tests Firebase-based features without backend API endpoints
"""

import requests
import json
import time
import base64
from datetime import datetime
import sys

class GuardianEyePhase2Tester:
    def __init__(self):
        # URLs from test credentials
        self.mobile_app_url = "https://device-security-hub-2.preview.emergentagent.com"
        self.dashboard_url = "https://device-security-hub-2.preview.emergentagent.com/dashboard.html"
        
        # Test credentials
        self.test_email = "test@guardianeye.com"
        self.test_password = "test123456"
        
        # Firebase config (from dashboard.html)
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

    def test_mobile_app_accessibility(self):
        """Test if mobile app is accessible"""
        try:
            response = requests.get(self.mobile_app_url, timeout=10)
            if response.status_code == 200:
                self.log_test("Mobile App Accessibility", "PASS", f"Status: {response.status_code}")
                return True
            else:
                self.log_test("Mobile App Accessibility", "FAIL", f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Mobile App Accessibility", "FAIL", f"Error: {str(e)}")
            return False

    def test_dashboard_accessibility(self):
        """Test if web dashboard is accessible"""
        try:
            response = requests.get(self.dashboard_url, timeout=10)
            if response.status_code == 200:
                # Check for key elements in dashboard
                content = response.text
                required_elements = [
                    "Guardian Eye Dashboard",
                    "firebase",
                    "Mark as Stolen",
                    "Device Location",
                    "Captured Photos"
                ]
                
                missing_elements = []
                for element in required_elements:
                    if element not in content:
                        missing_elements.append(element)
                
                if not missing_elements:
                    self.log_test("Dashboard Accessibility", "PASS", "All required elements found")
                    return True
                else:
                    self.log_test("Dashboard Accessibility", "FAIL", f"Missing elements: {missing_elements}")
                    return False
            else:
                self.log_test("Dashboard Accessibility", "FAIL", f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Dashboard Accessibility", "FAIL", f"Error: {str(e)}")
            return False

    def test_firebase_auth_endpoint(self):
        """Test Firebase Authentication endpoint"""
        try:
            # Firebase Auth REST API endpoint
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
                    self.log_test("Firebase Authentication", "PASS", f"User ID: {data['localId'][:10]}...")
                    return data
                else:
                    self.log_test("Firebase Authentication", "FAIL", "Missing token or user ID in response")
                    return None
            else:
                error_data = response.json() if response.content else {}
                error_msg = error_data.get('error', {}).get('message', 'Unknown error')
                self.log_test("Firebase Authentication", "FAIL", f"Status: {response.status_code}, Error: {error_msg}")
                return None
                
        except Exception as e:
            self.log_test("Firebase Authentication", "FAIL", f"Error: {str(e)}")
            return None

    def test_firebase_database_read(self, auth_data):
        """Test Firebase Realtime Database read access"""
        if not auth_data:
            self.log_test("Firebase Database Read", "SKIP", "No auth data available")
            return False
            
        try:
            # Test reading from devices path
            db_url = f"{self.firebase_config['databaseURL']}/devices.json"
            params = {"auth": auth_data['idToken']}
            
            response = requests.get(db_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Firebase Database Read", "PASS", f"Devices found: {len(data) if data else 0}")
                return True
            else:
                self.log_test("Firebase Database Read", "FAIL", f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Firebase Database Read", "FAIL", f"Error: {str(e)}")
            return False

    def test_device_registration_structure(self, auth_data):
        """Test device registration data structure"""
        if not auth_data:
            self.log_test("Device Registration Structure", "SKIP", "No auth data available")
            return False
            
        try:
            user_id = auth_data['localId']
            
            # Check user devices
            user_devices_url = f"{self.firebase_config['databaseURL']}/users/{user_id}/devices.json"
            params = {"auth": auth_data['idToken']}
            
            response = requests.get(user_devices_url, params=params, timeout=10)
            
            if response.status_code == 200:
                devices = response.json()
                if devices:
                    device_id = list(devices.keys())[0]
                    
                    # Check device details
                    device_url = f"{self.firebase_config['databaseURL']}/devices/{device_id}.json"
                    device_response = requests.get(device_url, params=params, timeout=10)
                    
                    if device_response.status_code == 200:
                        device_data = device_response.json()
                        
                        required_fields = ['deviceName', 'modelName', 'osName', 'status', 'lastSeen']
                        missing_fields = [field for field in required_fields if field not in device_data]
                        
                        if not missing_fields:
                            self.log_test("Device Registration Structure", "PASS", f"Device ID: {device_id[:10]}...")
                            return device_id
                        else:
                            self.log_test("Device Registration Structure", "FAIL", f"Missing fields: {missing_fields}")
                            return None
                    else:
                        self.log_test("Device Registration Structure", "FAIL", f"Device details not found: {device_response.status_code}")
                        return None
                else:
                    self.log_test("Device Registration Structure", "FAIL", "No devices registered for user")
                    return None
            else:
                self.log_test("Device Registration Structure", "FAIL", f"Status: {response.status_code}")
                return None
                
        except Exception as e:
            self.log_test("Device Registration Structure", "FAIL", f"Error: {str(e)}")
            return None

    def test_location_data_structure(self, auth_data, device_id):
        """Test GPS location data structure in Firebase"""
        if not auth_data or not device_id:
            self.log_test("Location Data Structure", "SKIP", "Missing auth data or device ID")
            return False
            
        try:
            # Check current location
            current_location_url = f"{self.firebase_config['databaseURL']}/devices/{device_id}/currentLocation.json"
            params = {"auth": auth_data['idToken']}
            
            response = requests.get(current_location_url, params=params, timeout=10)
            
            if response.status_code == 200:
                location_data = response.json()
                
                if location_data:
                    required_fields = ['latitude', 'longitude', 'timestamp']
                    missing_fields = [field for field in required_fields if field not in location_data]
                    
                    if not missing_fields:
                        self.log_test("Location Data Structure", "PASS", f"Lat: {location_data['latitude']}, Lng: {location_data['longitude']}")
                        return True
                    else:
                        self.log_test("Location Data Structure", "FAIL", f"Missing fields: {missing_fields}")
                        return False
                else:
                    self.log_test("Location Data Structure", "INFO", "No location data yet (expected for new device)")
                    return True
            else:
                self.log_test("Location Data Structure", "FAIL", f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Location Data Structure", "FAIL", f"Error: {str(e)}")
            return False

    def test_photo_data_structure(self, auth_data, device_id):
        """Test camera photo data structure in Firebase"""
        if not auth_data or not device_id:
            self.log_test("Photo Data Structure", "SKIP", "Missing auth data or device ID")
            return False
            
        try:
            # Check photos
            photos_url = f"{self.firebase_config['databaseURL']}/photos/{device_id}.json"
            params = {"auth": auth_data['idToken']}
            
            response = requests.get(photos_url, params=params, timeout=10)
            
            if response.status_code == 200:
                photos_data = response.json()
                
                if photos_data:
                    # Check first photo structure
                    first_photo = list(photos_data.values())[0]
                    required_fields = ['base64', 'timestamp', 'deviceId', 'captureType']
                    missing_fields = [field for field in required_fields if field not in first_photo]
                    
                    if not missing_fields:
                        self.log_test("Photo Data Structure", "PASS", f"Photos found: {len(photos_data)}")
                        return True
                    else:
                        self.log_test("Photo Data Structure", "FAIL", f"Missing fields: {missing_fields}")
                        return False
                else:
                    self.log_test("Photo Data Structure", "INFO", "No photos yet (expected for new device)")
                    return True
            else:
                self.log_test("Photo Data Structure", "FAIL", f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Photo Data Structure", "FAIL", f"Error: {str(e)}")
            return False

    def test_device_status_update(self, auth_data, device_id):
        """Test device status update functionality"""
        if not auth_data or not device_id:
            self.log_test("Device Status Update", "SKIP", "Missing auth data or device ID")
            return False
            
        try:
            # Update device status to STOLEN
            device_url = f"{self.firebase_config['databaseURL']}/devices/{device_id}.json"
            params = {"auth": auth_data['idToken']}
            
            update_data = {
                "status": "STOLEN",
                "markedStolenAt": int(time.time() * 1000)
            }
            
            response = requests.patch(device_url, json=update_data, params=params, timeout=10)
            
            if response.status_code == 200:
                # Wait a moment and check if status was updated
                time.sleep(2)
                
                check_response = requests.get(device_url, params=params, timeout=10)
                if check_response.status_code == 200:
                    device_data = check_response.json()
                    if device_data.get('status') == 'STOLEN':
                        self.log_test("Device Status Update", "PASS", "Status updated to STOLEN")
                        
                        # Reset to NORMAL for cleanup
                        reset_data = {"status": "NORMAL"}
                        requests.patch(device_url, json=reset_data, params=params, timeout=10)
                        
                        return True
                    else:
                        self.log_test("Device Status Update", "FAIL", f"Status not updated: {device_data.get('status')}")
                        return False
                else:
                    self.log_test("Device Status Update", "FAIL", f"Check failed: {check_response.status_code}")
                    return False
            else:
                self.log_test("Device Status Update", "FAIL", f"Update failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Device Status Update", "FAIL", f"Error: {str(e)}")
            return False

    def test_service_files_structure(self):
        """Test if Phase 2 service files exist and have correct structure"""
        try:
            import os
            
            service_files = [
                "/app/frontend/services/DeviceMonitor.ts",
                "/app/frontend/services/LocationService.ts", 
                "/app/frontend/services/CameraService.ts"
            ]
            
            missing_files = []
            for file_path in service_files:
                if not os.path.exists(file_path):
                    missing_files.append(file_path)
            
            if not missing_files:
                self.log_test("Service Files Structure", "PASS", "All Phase 2 service files exist")
                return True
            else:
                self.log_test("Service Files Structure", "FAIL", f"Missing files: {missing_files}")
                return False
                
        except Exception as e:
            self.log_test("Service Files Structure", "FAIL", f"Error: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all Phase 2 tests"""
        print("🔍 Starting Guardian Eye Phase 2 Testing - GPS Tracking & Camera Capture")
        print("=" * 70)
        print()
        
        # Test 1: Service files structure
        self.test_service_files_structure()
        
        # Test 2: App accessibility
        mobile_accessible = self.test_mobile_app_accessibility()
        dashboard_accessible = self.test_dashboard_accessibility()
        
        # Test 3: Firebase authentication
        auth_data = self.test_firebase_auth_endpoint()
        
        # Test 4: Database operations
        if auth_data:
            self.test_firebase_database_read(auth_data)
            device_id = self.test_device_registration_structure(auth_data)
            
            if device_id:
                self.test_location_data_structure(auth_data, device_id)
                self.test_photo_data_structure(auth_data, device_id)
                self.test_device_status_update(auth_data, device_id)
        
        # Summary
        print("=" * 70)
        print("📊 TEST SUMMARY")
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
        
        return success_rate >= 80

if __name__ == "__main__":
    tester = GuardianEyePhase2Tester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 Phase 2 testing completed successfully!")
        sys.exit(0)
    else:
        print("\n⚠️  Phase 2 testing completed with issues.")
        sys.exit(1)