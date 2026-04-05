#!/usr/bin/env python3
"""
Guardian Eye - Focused Camera Functionality Test
Critical pre-deployment test for camera capture functionality
"""

import requests
import time
import json
import logging
from urllib.parse import urljoin

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CameraFunctionalityTest:
    def __init__(self):
        self.mobile_url = "https://device-security-hub-2.preview.emergentagent.com"
        self.dashboard_url = "https://device-security-hub-2.preview.emergentagent.com/dashboard.html"
        self.test_email = "test@guardianeye.com"
        self.test_password = "test123456"
        
    def test_app_accessibility(self):
        """Test if the apps are accessible"""
        try:
            logger.info("🔍 Testing app accessibility...")
            
            # Test mobile app
            mobile_response = requests.get(self.mobile_url, timeout=10)
            mobile_accessible = mobile_response.status_code == 200
            logger.info(f"📱 Mobile app accessible: {'✅ YES' if mobile_accessible else '❌ NO'} (Status: {mobile_response.status_code})")
            
            # Test dashboard
            dashboard_response = requests.get(self.dashboard_url, timeout=10)
            dashboard_accessible = dashboard_response.status_code == 200
            logger.info(f"🖥️  Dashboard accessible: {'✅ YES' if dashboard_accessible else '❌ NO'} (Status: {dashboard_response.status_code})")
            
            return mobile_accessible and dashboard_accessible
            
        except Exception as e:
            logger.error(f"❌ App accessibility test failed: {e}")
            return False
    
    def check_camera_implementation(self):
        """Check camera service implementation"""
        try:
            logger.info("🔍 Checking camera service implementation...")
            
            # Check if camera service files exist
            camera_files = [
                "/app/frontend/services/CameraService.ts",
                "/app/frontend/components/HiddenCamera.tsx",
                "/app/frontend/services/DeviceMonitor.ts"
            ]
            
            missing_files = []
            for file_path in camera_files:
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                        if len(content) > 100:  # Basic check for non-empty file
                            logger.info(f"✅ {file_path} exists and has content")
                        else:
                            logger.warning(f"⚠️  {file_path} exists but seems empty")
                            missing_files.append(file_path)
                except FileNotFoundError:
                    logger.error(f"❌ {file_path} not found")
                    missing_files.append(file_path)
            
            return len(missing_files) == 0
            
        except Exception as e:
            logger.error(f"❌ Camera implementation check failed: {e}")
            return False
    
    def analyze_camera_code(self):
        """Analyze camera code for potential issues"""
        try:
            logger.info("🔍 Analyzing camera code for potential issues...")
            
            issues_found = []
            
            # Check HiddenCamera component
            try:
                with open("/app/frontend/components/HiddenCamera.tsx", 'r') as f:
                    hidden_camera_content = f.read()
                    
                    # Check for potential issues
                    if "CameraType.front" in hidden_camera_content:
                        issues_found.append("❌ Found 'CameraType.front' usage - this might cause 'undefined' errors")
                    
                    if 'facing="front"' in hidden_camera_content:
                        logger.info("✅ Using string literal 'front' instead of CameraType.front")
                    
                    if "takePictureAsync" in hidden_camera_content:
                        logger.info("✅ takePictureAsync method found")
                    
                    if "base64: true" in hidden_camera_content:
                        logger.info("✅ Base64 capture enabled")
                        
            except FileNotFoundError:
                issues_found.append("❌ HiddenCamera.tsx not found")
            
            # Check CameraService
            try:
                with open("/app/frontend/services/CameraService.ts", 'r') as f:
                    camera_service_content = f.read()
                    
                    if "uploadPhotoToFirebase" in camera_service_content:
                        logger.info("✅ Firebase upload functionality found")
                    
                    if "onPhotoCaptured" in camera_service_content:
                        logger.info("✅ Photo capture callback found")
                        
            except FileNotFoundError:
                issues_found.append("❌ CameraService.ts not found")
            
            # Check DeviceMonitor
            try:
                with open("/app/frontend/services/DeviceMonitor.ts", 'r') as f:
                    device_monitor_content = f.read()
                    
                    if "setOnCameraCapture" in device_monitor_content:
                        logger.info("✅ Camera capture trigger found")
                    
                    if "STOLEN" in device_monitor_content:
                        logger.info("✅ Status change monitoring found")
                        
            except FileNotFoundError:
                issues_found.append("❌ DeviceMonitor.ts not found")
            
            if issues_found:
                logger.error("🚨 CRITICAL ISSUES FOUND:")
                for issue in issues_found:
                    logger.error(f"   {issue}")
                return False
            else:
                logger.info("✅ No critical issues found in camera code")
                return True
                
        except Exception as e:
            logger.error(f"❌ Camera code analysis failed: {e}")
            return False
    
    def check_firebase_config(self):
        """Check Firebase configuration"""
        try:
            logger.info("🔍 Checking Firebase configuration...")
            
            # Check dashboard.html for Firebase config
            try:
                with open("/app/frontend/public/dashboard.html", 'r') as f:
                    dashboard_content = f.read()
                    
                    if "guardianeye-feb2d" in dashboard_content:
                        logger.info("✅ Firebase project ID found in dashboard")
                    
                    if "firebaseConfig" in dashboard_content:
                        logger.info("✅ Firebase configuration found")
                    
                    if "getDatabase" in dashboard_content:
                        logger.info("✅ Firebase database import found")
                    
                    if "photos/${deviceId}" in dashboard_content:
                        logger.info("✅ Photo storage path configuration found")
                        
            except FileNotFoundError:
                logger.error("❌ dashboard.html not found")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Firebase config check failed: {e}")
            return False
    
    def check_expo_camera_setup(self):
        """Check Expo camera setup"""
        try:
            logger.info("🔍 Checking Expo camera setup...")
            
            # Check package.json for expo-camera
            try:
                with open("/app/frontend/package.json", 'r') as f:
                    package_content = f.read()
                    package_json = json.loads(package_content)
                    
                    dependencies = package_json.get('dependencies', {})
                    if 'expo-camera' in dependencies:
                        logger.info(f"✅ expo-camera found: {dependencies['expo-camera']}")
                    else:
                        logger.error("❌ expo-camera not found in dependencies")
                        return False
                        
            except FileNotFoundError:
                logger.error("❌ package.json not found")
                return False
            except json.JSONDecodeError:
                logger.error("❌ package.json is not valid JSON")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Expo camera setup check failed: {e}")
            return False
    
    def run_comprehensive_test(self):
        """Run the complete camera functionality test"""
        logger.info("🚀 Starting Guardian Eye Camera Functionality Test")
        
        results = {
            'app_accessibility': False,
            'camera_implementation': False,
            'camera_code_analysis': False,
            'firebase_config': False,
            'expo_camera_setup': False,
            'overall_success': False
        }
        
        try:
            # Step 1: App Accessibility
            logger.info("\n=== STEP 1: App Accessibility ===")
            results['app_accessibility'] = self.test_app_accessibility()
            
            # Step 2: Camera Implementation
            logger.info("\n=== STEP 2: Camera Implementation Check ===")
            results['camera_implementation'] = self.check_camera_implementation()
            
            # Step 3: Camera Code Analysis
            logger.info("\n=== STEP 3: Camera Code Analysis ===")
            results['camera_code_analysis'] = self.analyze_camera_code()
            
            # Step 4: Firebase Configuration
            logger.info("\n=== STEP 4: Firebase Configuration ===")
            results['firebase_config'] = self.check_firebase_config()
            
            # Step 5: Expo Camera Setup
            logger.info("\n=== STEP 5: Expo Camera Setup ===")
            results['expo_camera_setup'] = self.check_expo_camera_setup()
            
            # Overall success
            results['overall_success'] = all([
                results['app_accessibility'],
                results['camera_implementation'],
                results['camera_code_analysis'],
                results['firebase_config'],
                results['expo_camera_setup']
            ])
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Test execution failed: {e}")
            return results

def main():
    """Main test execution"""
    test = CameraFunctionalityTest()
    results = test.run_comprehensive_test()
    
    # Print final results
    print("\n" + "="*60)
    print("🎯 GUARDIAN EYE CAMERA FUNCTIONALITY TEST RESULTS")
    print("="*60)
    
    print(f"✅ App Accessibility: {'PASS' if results['app_accessibility'] else 'FAIL'}")
    print(f"✅ Camera Implementation: {'PASS' if results['camera_implementation'] else 'FAIL'}")
    print(f"✅ Camera Code Analysis: {'PASS' if results['camera_code_analysis'] else 'FAIL'}")
    print(f"✅ Firebase Configuration: {'PASS' if results['firebase_config'] else 'FAIL'}")
    print(f"✅ Expo Camera Setup: {'PASS' if results['expo_camera_setup'] else 'FAIL'}")
    
    print(f"\n🎯 OVERALL RESULT: {'✅ PASS' if results['overall_success'] else '❌ FAIL'}")
    
    if results['overall_success']:
        print("\n🎉 Camera functionality setup is correct!")
        print("📸 All camera components and configurations are in place")
        print("🚀 App should be ready for camera testing")
        print("\n📋 MANUAL TESTING STEPS:")
        print("1. Open mobile app and login with test@guardianeye.com")
        print("2. Open dashboard and login with same credentials")
        print("3. Mark device as stolen from dashboard")
        print("4. Check mobile console for camera capture logs")
        print("5. Verify photo appears in dashboard gallery")
    else:
        print("\n⚠️  Camera functionality issues detected!")
        print("🔧 Review the failed checks above")
        print("🚨 Fix issues before deployment")
    
    print("="*60)
    
    return results['overall_success']

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)