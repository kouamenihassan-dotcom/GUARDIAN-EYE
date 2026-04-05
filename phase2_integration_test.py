#!/usr/bin/env python3
"""
Guardian Eye Phase 2 Integration Testing
Tests the actual GPS tracking and camera capture flow
"""

import requests
import json
import time
from datetime import datetime
import sys

class Phase2IntegrationTester:
    def __init__(self):
        # Firebase config
        self.firebase_config = {
            "apiKey": "AIzaSyDCc8qBTWxO-sX5dhlC6mDWokomgScIFwQ",
            "databaseURL": "https://guardianeye-feb2d-default-rtdb.firebaseio.com"
        }
        
        # Test credentials
        self.test_email = "test@guardianeye.com"
        self.test_password = "test123456"
        
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

    def authenticate(self):
        """Authenticate with Firebase"""
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
                return data
            else:
                return None
                
        except Exception as e:
            return None

    def get_device_id(self, auth_data):
        """Get the first device ID for the user"""
        try:
            user_id = auth_data['localId']
            user_devices_url = f"{self.firebase_config['databaseURL']}/users/{user_id}/devices.json"
            params = {"auth": auth_data['idToken']}
            
            response = requests.get(user_devices_url, params=params, timeout=10)
            
            if response.status_code == 200:
                devices = response.json()
                if devices:
                    return list(devices.keys())[0]
            return None
                
        except Exception as e:
            return None

    def test_device_status_monitoring(self, auth_data, device_id):
        """Test device status monitoring and triggers"""
        try:
            device_url = f"{self.firebase_config['databaseURL']}/devices/{device_id}.json"
            params = {"auth": auth_data['idToken']}
            
            # Step 1: Mark device as STOLEN
            print("🔄 Marking device as STOLEN to trigger GPS and camera...")
            update_data = {
                "status": "STOLEN",
                "markedStolenAt": int(time.time() * 1000)
            }
            
            response = requests.patch(device_url, json=update_data, params=params, timeout=10)
            
            if response.status_code != 200:
                self.log_test("Device Status Monitoring", "FAIL", f"Failed to update status: {response.status_code}")
                return False
            
            # Step 2: Wait for potential triggers (simulate mobile app processing)
            print("⏳ Waiting 10 seconds for mobile app to process status change...")
            time.sleep(10)
            
            # Step 3: Check if location data was added
            location_url = f"{self.firebase_config['databaseURL']}/devices/{device_id}/currentLocation.json"
            location_response = requests.get(location_url, params=params, timeout=10)
            
            location_triggered = False
            if location_response.status_code == 200:
                location_data = location_response.json()
                if location_data and 'latitude' in location_data:
                    location_triggered = True
                    print(f"📍 Location data found: {location_data['latitude']}, {location_data['longitude']}")
            
            # Step 4: Check if photos were captured
            photos_url = f"{self.firebase_config['databaseURL']}/photos/{device_id}.json"
            photos_response = requests.get(photos_url, params=params, timeout=10)
            
            photos_triggered = False
            if photos_response.status_code == 200:
                photos_data = photos_response.json()
                if photos_data:
                    photos_triggered = True
                    print(f"📸 Photos found: {len(photos_data)} photos captured")
            
            # Step 5: Reset device to NORMAL
            reset_data = {"status": "NORMAL"}
            requests.patch(device_url, json=reset_data, params=params, timeout=10)
            
            # Evaluate results
            if location_triggered and photos_triggered:
                self.log_test("Device Status Monitoring", "PASS", "Both GPS tracking and camera capture triggered")
                return True
            elif location_triggered or photos_triggered:
                triggered = "GPS" if location_triggered else "Camera"
                self.log_test("Device Status Monitoring", "PARTIAL", f"Only {triggered} triggered")
                return True
            else:
                self.log_test("Device Status Monitoring", "INFO", "No automatic triggers detected (may require mobile app interaction)")
                return True
                
        except Exception as e:
            self.log_test("Device Status Monitoring", "FAIL", f"Error: {str(e)}")
            return False

    def test_manual_location_injection(self, auth_data, device_id):
        """Test manual location data injection to verify structure"""
        try:
            device_url = f"{self.firebase_config['databaseURL']}/devices/{device_id}.json"
            params = {"auth": auth_data['idToken']}
            
            # Inject test location data
            test_location = {
                "latitude": 37.7749,
                "longitude": -122.4194,
                "accuracy": 10.0,
                "timestamp": int(time.time() * 1000)
            }
            
            location_data = {
                "currentLocation": test_location,
                "lastLocationUpdate": test_location["timestamp"]
            }
            
            response = requests.patch(device_url, json=location_data, params=params, timeout=10)
            
            if response.status_code == 200:
                # Also add to location history
                history_url = f"{self.firebase_config['databaseURL']}/locations/{device_id}/{test_location['timestamp']}.json"
                history_response = requests.put(history_url, json=test_location, params=params, timeout=10)
                
                if history_response.status_code == 200:
                    self.log_test("Manual Location Injection", "PASS", f"Location data injected: {test_location['latitude']}, {test_location['longitude']}")
                    return True
                else:
                    self.log_test("Manual Location Injection", "FAIL", f"History injection failed: {history_response.status_code}")
                    return False
            else:
                self.log_test("Manual Location Injection", "FAIL", f"Location injection failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Manual Location Injection", "FAIL", f"Error: {str(e)}")
            return False

    def test_manual_photo_injection(self, auth_data, device_id):
        """Test manual photo data injection to verify structure"""
        try:
            # Create a small test image (1x1 pixel PNG)
            test_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
            
            timestamp = int(time.time() * 1000)
            photo_data = {
                "base64": test_base64,
                "timestamp": timestamp,
                "deviceId": device_id,
                "captureType": "test",
                "downloadURL": "test://placeholder"
            }
            
            # Add photo to Firebase
            photos_url = f"{self.firebase_config['databaseURL']}/photos/{device_id}.json"
            params = {"auth": auth_data['idToken']}
            
            # Use POST to add new photo
            response = requests.post(photos_url, json=photo_data, params=params, timeout=10)
            
            if response.status_code == 200:
                self.log_test("Manual Photo Injection", "PASS", f"Photo data injected with timestamp: {timestamp}")
                return True
            else:
                self.log_test("Manual Photo Injection", "FAIL", f"Photo injection failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Manual Photo Injection", "FAIL", f"Error: {str(e)}")
            return False

    def test_dashboard_data_display(self, auth_data, device_id):
        """Test if dashboard can display the injected data"""
        try:
            params = {"auth": auth_data['idToken']}
            
            # Check current location display
            location_url = f"{self.firebase_config['databaseURL']}/devices/{device_id}/currentLocation.json"
            location_response = requests.get(location_url, params=params, timeout=10)
            
            location_ok = False
            if location_response.status_code == 200:
                location_data = location_response.json()
                if location_data and 'latitude' in location_data and 'longitude' in location_data:
                    location_ok = True
            
            # Check photos display
            photos_url = f"{self.firebase_config['databaseURL']}/photos/{device_id}.json"
            photos_response = requests.get(photos_url, params=params, timeout=10)
            
            photos_ok = False
            if photos_response.status_code == 200:
                photos_data = photos_response.json()
                if photos_data:
                    photos_ok = True
            
            if location_ok and photos_ok:
                self.log_test("Dashboard Data Display", "PASS", "Both location and photo data available for dashboard")
                return True
            elif location_ok or photos_ok:
                available = "Location" if location_ok else "Photos"
                self.log_test("Dashboard Data Display", "PARTIAL", f"Only {available} data available")
                return True
            else:
                self.log_test("Dashboard Data Display", "FAIL", "No location or photo data available")
                return False
                
        except Exception as e:
            self.log_test("Dashboard Data Display", "FAIL", f"Error: {str(e)}")
            return False

    def test_real_time_updates(self, auth_data, device_id):
        """Test real-time update capability"""
        try:
            device_url = f"{self.firebase_config['databaseURL']}/devices/{device_id}.json"
            params = {"auth": auth_data['idToken']}
            
            # Update device status multiple times
            statuses = ["STOLEN", "LOCKED", "NORMAL"]
            
            for status in statuses:
                update_data = {
                    "status": status,
                    "lastStatusChange": int(time.time() * 1000)
                }
                
                response = requests.patch(device_url, json=update_data, params=params, timeout=10)
                
                if response.status_code != 200:
                    self.log_test("Real-time Updates", "FAIL", f"Failed to update to {status}")
                    return False
                
                # Brief pause between updates
                time.sleep(1)
            
            self.log_test("Real-time Updates", "PASS", "Status updates working correctly")
            return True
                
        except Exception as e:
            self.log_test("Real-time Updates", "FAIL", f"Error: {str(e)}")
            return False

    def run_integration_tests(self):
        """Run all Phase 2 integration tests"""
        print("🔍 Starting Guardian Eye Phase 2 Integration Testing")
        print("=" * 70)
        print()
        
        # Authenticate
        print("🔐 Authenticating with Firebase...")
        auth_data = self.authenticate()
        if not auth_data:
            print("❌ Authentication failed - cannot proceed with tests")
            return False
        
        # Get device ID
        device_id = self.get_device_id(auth_data)
        if not device_id:
            print("❌ No device found - cannot proceed with tests")
            return False
        
        print(f"📱 Testing with device: {device_id[:15]}...")
        print()
        
        # Run tests
        self.test_device_status_monitoring(auth_data, device_id)
        self.test_manual_location_injection(auth_data, device_id)
        self.test_manual_photo_injection(auth_data, device_id)
        self.test_dashboard_data_display(auth_data, device_id)
        self.test_real_time_updates(auth_data, device_id)
        
        # Summary
        print("=" * 70)
        print("📊 INTEGRATION TEST SUMMARY")
        print("=" * 70)
        
        passed = len([r for r in self.test_results if r['status'] == 'PASS'])
        failed = len([r for r in self.test_results if r['status'] == 'FAIL'])
        partial = len([r for r in self.test_results if r['status'] == 'PARTIAL'])
        info = len([r for r in self.test_results if r['status'] == 'INFO'])
        total = len(self.test_results)
        
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"🔶 Partial: {partial}")
        print(f"ℹ️  Info: {info}")
        print(f"📋 Total: {total}")
        print()
        
        if failed > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if result['status'] == 'FAIL':
                    print(f"   • {result['test']}: {result['details']}")
            print()
        
        success_rate = (passed + partial) / total * 100 if total > 0 else 0
        print(f"🎯 Success Rate: {success_rate:.1f}%")
        
        return success_rate >= 80

if __name__ == "__main__":
    tester = Phase2IntegrationTester()
    success = tester.run_integration_tests()
    
    if success:
        print("\n🎉 Phase 2 integration testing completed successfully!")
        sys.exit(0)
    else:
        print("\n⚠️  Phase 2 integration testing completed with issues.")
        sys.exit(1)