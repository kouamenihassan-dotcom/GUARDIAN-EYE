#!/usr/bin/env python3
"""
Manual Firebase Testing for Guardian Eye
Tests Firebase authentication and functionality manually
"""

import requests
import json
import time

class ManualFirebaseTest:
    def __init__(self):
        self.mobile_url = "https://device-security-hub-2.preview.emergentagent.com"
        self.dashboard_url = "https://device-security-hub-2.preview.emergentagent.com/dashboard.html"
        self.test_email = "test@guardianeye.com"
        self.test_password = "test123456"
        
    def test_url_accessibility(self):
        """Test if URLs are accessible"""
        print("Testing URL Accessibility...")
        
        # Test mobile app
        try:
            response = requests.get(self.mobile_url, timeout=10)
            if response.status_code == 200:
                print(f"✅ Mobile App URL accessible: {response.status_code}")
                if "Guardian Eye" in response.text or "guardian" in response.text.lower():
                    print("✅ Mobile App contains Guardian Eye content")
                else:
                    print("⚠️  Mobile App may not contain expected content")
            else:
                print(f"❌ Mobile App URL failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Mobile App URL error: {e}")
        
        # Test dashboard
        try:
            response = requests.get(self.dashboard_url, timeout=10)
            if response.status_code == 200:
                print(f"✅ Dashboard URL accessible: {response.status_code}")
                if "Guardian Eye" in response.text and "dashboard" in response.text.lower():
                    print("✅ Dashboard contains expected content")
                    
                    # Check for Firebase configuration
                    if "firebase" in response.text.lower():
                        print("✅ Dashboard contains Firebase configuration")
                    else:
                        print("⚠️  Dashboard may not contain Firebase configuration")
                        
                    # Check for login form
                    if 'id="email"' in response.text and 'id="password"' in response.text:
                        print("✅ Dashboard contains login form")
                    else:
                        print("❌ Dashboard missing login form")
                        
                else:
                    print("❌ Dashboard does not contain expected content")
            else:
                print(f"❌ Dashboard URL failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Dashboard URL error: {e}")
    
    def test_firebase_config(self):
        """Test Firebase configuration"""
        print("\nTesting Firebase Configuration...")
        
        try:
            response = requests.get(self.dashboard_url, timeout=10)
            content = response.text
            
            # Check for Firebase config
            firebase_configs = [
                "AIzaSyDCc8qBTWxO-sX5dhlC6mDWokomgScIFwQ",  # API Key
                "guardianeye-feb2d.firebaseapp.com",  # Auth Domain
                "https://guardianeye-feb2d-default-rtdb.firebaseio.com",  # Database URL
                "guardianeye-feb2d",  # Project ID
            ]
            
            for config in firebase_configs:
                if config in content:
                    print(f"✅ Firebase config found: {config[:20]}...")
                else:
                    print(f"❌ Firebase config missing: {config[:20]}...")
                    
        except Exception as e:
            print(f"❌ Error checking Firebase config: {e}")
    
    def test_mobile_app_structure(self):
        """Test mobile app structure"""
        print("\nTesting Mobile App Structure...")
        
        try:
            response = requests.get(self.mobile_url, timeout=10)
            content = response.text
            
            # Check for React/Expo structure
            react_indicators = [
                "expo-router",
                "react",
                "_expo",
                "bundle.js",
                "index.js"
            ]
            
            found_indicators = []
            for indicator in react_indicators:
                if indicator in content.lower():
                    found_indicators.append(indicator)
            
            if found_indicators:
                print(f"✅ Mobile app appears to be React/Expo based: {found_indicators}")
            else:
                print("⚠️  Mobile app structure unclear")
                
            # Check for authentication elements
            auth_indicators = [
                "sign",
                "login",
                "email",
                "password",
                "auth"
            ]
            
            found_auth = []
            for indicator in auth_indicators:
                if indicator in content.lower():
                    found_auth.append(indicator)
            
            if found_auth:
                print(f"✅ Authentication elements found: {found_auth}")
            else:
                print("❌ No authentication elements found")
                
        except Exception as e:
            print(f"❌ Error checking mobile app structure: {e}")
    
    def test_firebase_endpoints(self):
        """Test Firebase endpoints"""
        print("\nTesting Firebase Endpoints...")
        
        # Test Firebase Auth endpoint
        auth_url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"
        try:
            # This should return a 400 error for missing API key, which means endpoint is accessible
            response = requests.post(auth_url, json={}, timeout=10)
            if response.status_code == 400:
                print("✅ Firebase Auth endpoint accessible")
            else:
                print(f"⚠️  Firebase Auth endpoint returned: {response.status_code}")
        except Exception as e:
            print(f"❌ Firebase Auth endpoint error: {e}")
        
        # Test Firebase Database endpoint
        db_url = "https://guardianeye-feb2d-default-rtdb.firebaseio.com/.json"
        try:
            response = requests.get(db_url, timeout=10)
            if response.status_code in [200, 401, 403]:  # 401/403 means auth required, which is expected
                print("✅ Firebase Database endpoint accessible")
            else:
                print(f"⚠️  Firebase Database endpoint returned: {response.status_code}")
        except Exception as e:
            print(f"❌ Firebase Database endpoint error: {e}")
    
    def run_manual_tests(self):
        """Run all manual tests"""
        print("Starting Manual Firebase Testing for Guardian Eye...")
        print("=" * 60)
        
        self.test_url_accessibility()
        self.test_firebase_config()
        self.test_mobile_app_structure()
        self.test_firebase_endpoints()
        
        print("\n" + "=" * 60)
        print("Manual Testing Complete")
        print("=" * 60)

if __name__ == "__main__":
    tester = ManualFirebaseTest()
    tester.run_manual_tests()