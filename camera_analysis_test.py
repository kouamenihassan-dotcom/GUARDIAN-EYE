#!/usr/bin/env python3
"""
Guardian Eye - Camera Functionality Analysis & Manual Test Guide
Critical pre-deployment test for camera capture functionality
"""

import json
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CameraFunctionalityAnalysis:
    def __init__(self):
        self.test_email = "test@guardianeye.com"
        self.test_password = "test123456"
        self.mobile_url = "https://device-security-hub-2.preview.emergentagent.com"
        self.dashboard_url = "https://device-security-hub-2.preview.emergentagent.com/dashboard.html"
        
    def analyze_hidden_camera_component(self):
        """Analyze HiddenCamera component for potential issues"""
        try:
            logger.info("🔍 Analyzing HiddenCamera component...")
            
            with open("/app/frontend/components/HiddenCamera.tsx", 'r') as f:
                content = f.read()
            
            issues = []
            good_practices = []
            
            # Check for CameraType usage issues
            if "CameraType.front" in content:
                issues.append("❌ CRITICAL: Found 'CameraType.front' - this will cause 'Cannot read properties of undefined (reading 'front')' error")
            elif 'facing="front"' in content:
                good_practices.append("✅ Using string literal 'front' instead of CameraType.front")
            
            # Check for proper imports
            if "import { CameraView, useCameraPermissions } from 'expo-camera'" in content:
                good_practices.append("✅ Correct expo-camera imports")
            
            # Check for takePictureAsync
            if "takePictureAsync" in content:
                good_practices.append("✅ takePictureAsync method implemented")
            
            # Check for base64 capture
            if "base64: true" in content:
                good_practices.append("✅ Base64 capture enabled")
            
            # Check for permission handling
            if "useCameraPermissions" in content:
                good_practices.append("✅ Camera permissions handled")
            
            # Check for error handling
            if "try" in content and "catch" in content:
                good_practices.append("✅ Error handling implemented")
            
            # Check for console logging
            if "console.log('📸 Capturing actual photo..." in content:
                good_practices.append("✅ Capture logging implemented")
            
            if "console.log('✅ Photo captured successfully" in content:
                good_practices.append("✅ Success logging implemented")
            
            return issues, good_practices
            
        except FileNotFoundError:
            return ["❌ CRITICAL: HiddenCamera.tsx not found"], []
        except Exception as e:
            return [f"❌ Error analyzing HiddenCamera: {e}"], []
    
    def analyze_camera_service(self):
        """Analyze CameraService for Firebase integration"""
        try:
            logger.info("🔍 Analyzing CameraService...")
            
            with open("/app/frontend/services/CameraService.ts", 'r') as f:
                content = f.read()
            
            issues = []
            good_practices = []
            
            # Check Firebase imports
            if "firebase/storage" in content and "firebase/database" in content:
                good_practices.append("✅ Firebase Storage and Database imports found")
            
            # Check upload functionality
            if "uploadPhotoToFirebase" in content:
                good_practices.append("✅ Firebase upload function implemented")
            
            # Check photo path structure
            if "photos/${deviceId}/${timestamp}.jpg" in content:
                good_practices.append("✅ Correct photo storage path structure")
            
            # Check base64 handling
            if "base64" in content:
                good_practices.append("✅ Base64 photo handling implemented")
            
            # Check callback mechanism
            if "onPhotoCaptured" in content:
                good_practices.append("✅ Photo capture callback implemented")
            
            return issues, good_practices
            
        except FileNotFoundError:
            return ["❌ CRITICAL: CameraService.ts not found"], []
        except Exception as e:
            return [f"❌ Error analyzing CameraService: {e}"], []
    
    def analyze_device_monitor(self):
        """Analyze DeviceMonitor for status change handling"""
        try:
            logger.info("🔍 Analyzing DeviceMonitor...")
            
            with open("/app/frontend/services/DeviceMonitor.ts", 'r') as f:
                content = f.read()
            
            issues = []
            good_practices = []
            
            # Check status change handling
            if "STOLEN" in content:
                good_practices.append("✅ STOLEN status handling implemented")
            
            # Check camera trigger
            if "setOnCameraCapture" in content:
                good_practices.append("✅ Camera capture trigger mechanism implemented")
            
            # Check Firebase listener
            if "onValue" in content:
                good_practices.append("✅ Firebase real-time listener implemented")
            
            return issues, good_practices
            
        except FileNotFoundError:
            return ["❌ CRITICAL: DeviceMonitor.ts not found"], []
        except Exception as e:
            return [f"❌ Error analyzing DeviceMonitor: {e}"], []
    
    def analyze_home_screen_integration(self):
        """Analyze home screen camera integration"""
        try:
            logger.info("🔍 Analyzing home screen camera integration...")
            
            with open("/app/frontend/app/home.tsx", 'r') as f:
                content = f.read()
            
            issues = []
            good_practices = []
            
            # Check HiddenCamera import and usage
            if "import { HiddenCamera }" in content:
                good_practices.append("✅ HiddenCamera component imported")
            
            if "<HiddenCamera" in content:
                good_practices.append("✅ HiddenCamera component used in JSX")
            
            # Check state management
            if "shouldCapturePhoto" in content:
                good_practices.append("✅ Photo capture state management implemented")
            
            # Check callback handling
            if "handlePhotoCapture" in content:
                good_practices.append("✅ Photo capture handler implemented")
            
            return issues, good_practices
            
        except FileNotFoundError:
            return ["❌ CRITICAL: home.tsx not found"], []
        except Exception as e:
            return [f"❌ Error analyzing home screen: {e}"], []
    
    def check_expo_camera_dependency(self):
        """Check expo-camera dependency"""
        try:
            logger.info("🔍 Checking expo-camera dependency...")
            
            with open("/app/frontend/package.json", 'r') as f:
                package_data = json.load(f)
            
            dependencies = package_data.get('dependencies', {})
            
            if 'expo-camera' in dependencies:
                version = dependencies['expo-camera']
                return [], [f"✅ expo-camera dependency found: {version}"]
            else:
                return ["❌ CRITICAL: expo-camera dependency missing"], []
                
        except FileNotFoundError:
            return ["❌ CRITICAL: package.json not found"], []
        except Exception as e:
            return [f"❌ Error checking dependencies: {e}"], []
    
    def generate_manual_test_guide(self):
        """Generate manual testing guide"""
        return f"""
🧪 MANUAL TESTING GUIDE - CAMERA FUNCTIONALITY
===============================================

📋 Test Credentials:
   Email: {self.test_email}
   Password: {self.test_password}

🔗 Test URLs:
   Mobile App: {self.mobile_url}
   Dashboard: {self.dashboard_url}

📱 STEP-BY-STEP TESTING PROCEDURE:

1️⃣ SETUP & LOGIN
   • Open mobile app in browser
   • Login with test credentials
   • Verify app loads without errors
   • Open browser console (F12)
   • Look for any errors related to "CameraType", "undefined", or HiddenCamera

2️⃣ DASHBOARD LOGIN
   • Open dashboard in new tab
   • Login with same credentials
   • Select device from list
   • Click "Manage" button

3️⃣ TRIGGER CAMERA CAPTURE
   • Click "Mark as Stolen" button
   • Confirm the action
   • Switch back to mobile app tab
   • Check console for these messages:
     ✅ "📸 Capturing actual photo..."
     ✅ "✅ Photo captured successfully - length: XXXX"
     ❌ NO errors about "CameraType", "undefined", or "reading 'front'"

4️⃣ VERIFY PHOTO UPLOAD
   • Wait 5-10 seconds for photo upload
   • In dashboard, scroll to "📸 Captured Photos" section
   • Verify:
     ✅ Photo gallery is NOT empty
     ✅ At least one photo appears
     ✅ Photo has timestamp
     ✅ Photo displays correctly (not broken image)

5️⃣ VERIFY FIREBASE DATA
   • Check console logs for:
     ✅ "Photo uploaded to Firebase: photos/{{deviceId}}/{{timestamp}}.jpg"
     ❌ No upload errors
     ❌ No Firebase storage errors

🎯 SUCCESS CRITERIA:
   ✅ No "CameraType.front undefined" errors
   ✅ Console shows "📸 Capturing actual photo..."
   ✅ Console shows "✅ Photo captured successfully"
   ✅ Photo appears in dashboard gallery
   ✅ Photo has base64 data
   ✅ No console errors

🚨 FAILURE INDICATORS:
   ❌ "Cannot read properties of undefined (reading 'front')"
   ❌ "CameraType is not defined"
   ❌ Photo gallery shows "No photos captured yet"
   ❌ Any errors in console related to camera
   ❌ Firebase upload errors

💡 TROUBLESHOOTING:
   • If camera permission denied: Grant camera access in browser
   • If no photos appear: Check Firebase console for storage errors
   • If "CameraType" errors: Check HiddenCamera.tsx implementation
   • If upload fails: Check Firebase configuration and network
"""
    
    def run_analysis(self):
        """Run complete camera functionality analysis"""
        logger.info("🚀 Starting Guardian Eye Camera Functionality Analysis")
        
        all_issues = []
        all_good_practices = []
        
        # Analyze each component
        components = [
            ("HiddenCamera Component", self.analyze_hidden_camera_component),
            ("CameraService", self.analyze_camera_service),
            ("DeviceMonitor", self.analyze_device_monitor),
            ("Home Screen Integration", self.analyze_home_screen_integration),
            ("Expo Camera Dependency", self.check_expo_camera_dependency)
        ]
        
        for component_name, analyzer in components:
            logger.info(f"\n=== {component_name.upper()} ===")
            issues, good_practices = analyzer()
            
            if issues:
                logger.error(f"🚨 Issues in {component_name}:")
                for issue in issues:
                    logger.error(f"   {issue}")
                all_issues.extend(issues)
            
            if good_practices:
                logger.info(f"✅ Good practices in {component_name}:")
                for practice in good_practices:
                    logger.info(f"   {practice}")
                all_good_practices.extend(good_practices)
        
        return all_issues, all_good_practices

def main():
    """Main analysis execution"""
    analyzer = CameraFunctionalityAnalysis()
    issues, good_practices = analyzer.run_analysis()
    
    # Print final results
    print("\n" + "="*70)
    print("🎯 GUARDIAN EYE CAMERA FUNCTIONALITY ANALYSIS RESULTS")
    print("="*70)
    
    if issues:
        print("\n🚨 CRITICAL ISSUES FOUND:")
        for issue in issues:
            print(f"   {issue}")
    
    print(f"\n✅ GOOD PRACTICES FOUND ({len(good_practices)}):")
    for practice in good_practices:
        print(f"   {practice}")
    
    # Overall assessment
    critical_issues = [issue for issue in issues if "CRITICAL" in issue]
    
    if critical_issues:
        print(f"\n🎯 OVERALL RESULT: ❌ FAIL")
        print(f"🚨 {len(critical_issues)} critical issues must be fixed before deployment")
    else:
        print(f"\n🎯 OVERALL RESULT: ✅ PASS")
        print("📸 Camera functionality implementation looks correct")
        print("🚀 Ready for manual testing")
    
    # Print manual testing guide
    print(analyzer.generate_manual_test_guide())
    
    print("="*70)
    
    return len(critical_issues) == 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)