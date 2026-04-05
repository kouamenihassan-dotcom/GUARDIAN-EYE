#!/usr/bin/env python3
"""
Guardian Eye - Camera Functionality Test
Critical pre-deployment test for camera capture functionality
"""

import requests
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CameraFunctionalityTest:
    def __init__(self):
        self.mobile_url = "https://device-security-hub-2.preview.emergentagent.com"
        self.dashboard_url = "https://device-security-hub-2.preview.emergentagent.com/dashboard.html"
        self.test_email = "test@guardianeye.com"
        self.test_password = "test123456"
        self.mobile_driver = None
        self.dashboard_driver = None
        
    def setup_drivers(self):
        """Setup Chrome drivers for mobile and dashboard"""
        try:
            # Mobile driver with mobile user agent
            mobile_options = Options()
            mobile_options.add_argument("--no-sandbox")
            mobile_options.add_argument("--disable-dev-shm-usage")
            mobile_options.add_argument("--disable-gpu")
            mobile_options.add_argument("--use-fake-ui-for-media-stream")
            mobile_options.add_argument("--use-fake-device-for-media-stream")
            mobile_options.add_argument("--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1")
            mobile_options.add_experimental_option("mobileEmulation", {
                "deviceMetrics": {"width": 390, "height": 844, "pixelRatio": 3.0},
                "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15"
            })
            
            self.mobile_driver = webdriver.Chrome(options=mobile_options)
            logger.info("✅ Mobile driver setup complete")
            
            # Dashboard driver
            dashboard_options = Options()
            dashboard_options.add_argument("--no-sandbox")
            dashboard_options.add_argument("--disable-dev-shm-usage")
            dashboard_options.add_argument("--disable-gpu")
            
            self.dashboard_driver = webdriver.Chrome(options=dashboard_options)
            logger.info("✅ Dashboard driver setup complete")
            
            return True
        except Exception as e:
            logger.error(f"❌ Failed to setup drivers: {e}")
            return False
    
    def test_mobile_login(self):
        """Test mobile app login"""
        try:
            logger.info("🔍 Testing mobile app login...")
            self.mobile_driver.get(self.mobile_url)
            
            # Wait for page to load
            WebDriverWait(self.mobile_driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Check for login elements
            email_input = WebDriverWait(self.mobile_driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email'], input[placeholder*='email'], input[name='email']"))
            )
            
            password_input = self.mobile_driver.find_element(By.CSS_SELECTOR, "input[type='password'], input[placeholder*='password'], input[name='password']")
            
            # Enter credentials
            email_input.clear()
            email_input.send_keys(self.test_email)
            password_input.clear()
            password_input.send_keys(self.test_password)
            
            # Find and click login button
            login_button = self.mobile_driver.find_element(By.CSS_SELECTOR, "button[type='submit'], button:contains('Sign In'), button:contains('Login')")
            login_button.click()
            
            # Wait for login to complete
            time.sleep(3)
            
            # Check for successful login (look for home screen elements)
            try:
                WebDriverWait(self.mobile_driver, 10).until(
                    EC.any_of(
                        EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Guardian Eye')]")),
                        EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Device Status')]")),
                        EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Home')]"))
                    )
                )
                logger.info("✅ Mobile login successful")
                return True
            except TimeoutException:
                logger.error("❌ Mobile login failed - home screen not found")
                return False
                
        except Exception as e:
            logger.error(f"❌ Mobile login error: {e}")
            return False
    
    def test_dashboard_login(self):
        """Test dashboard login"""
        try:
            logger.info("🔍 Testing dashboard login...")
            self.dashboard_driver.get(self.dashboard_url)
            
            # Wait for login form
            email_input = WebDriverWait(self.dashboard_driver, 10).until(
                EC.presence_of_element_located((By.ID, "email"))
            )
            
            password_input = self.dashboard_driver.find_element(By.ID, "password")
            
            # Enter credentials
            email_input.clear()
            email_input.send_keys(self.test_email)
            password_input.clear()
            password_input.send_keys(self.test_password)
            
            # Submit form
            login_form = self.dashboard_driver.find_element(By.ID, "loginForm")
            login_form.submit()
            
            # Wait for dashboard to load
            WebDriverWait(self.dashboard_driver, 10).until(
                EC.presence_of_element_located((By.ID, "dashboard"))
            )
            
            logger.info("✅ Dashboard login successful")
            return True
            
        except Exception as e:
            logger.error(f"❌ Dashboard login error: {e}")
            return False
    
    def trigger_camera_capture(self):
        """Trigger camera capture by marking device as stolen"""
        try:
            logger.info("🔍 Triggering camera capture...")
            
            # Find and click on a device to manage
            device_manage_button = WebDriverWait(self.dashboard_driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Manage')]"))
            )
            device_manage_button.click()
            
            # Wait for device control panel
            time.sleep(2)
            
            # Click "Mark as Stolen" button
            stolen_button = WebDriverWait(self.dashboard_driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Mark as Stolen')]"))
            )
            stolen_button.click()
            
            # Confirm the action
            self.dashboard_driver.switch_to.alert.accept()
            
            logger.info("✅ Device marked as stolen - camera capture triggered")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to trigger camera capture: {e}")
            return False
    
    def check_mobile_console_logs(self):
        """Check mobile app console for camera-related logs"""
        try:
            logger.info("🔍 Checking mobile console logs...")
            
            # Get console logs
            logs = self.mobile_driver.get_log('browser')
            
            camera_logs = []
            error_logs = []
            
            for log in logs:
                message = log['message']
                if any(keyword in message.lower() for keyword in ['camera', 'photo', 'capture']):
                    camera_logs.append(message)
                    
                if any(error in message.lower() for error in ['cameratype', 'undefined', 'error']):
                    error_logs.append(message)
            
            # Check for expected success messages
            success_indicators = [
                "📸 Capturing actual photo...",
                "✅ Photo captured successfully",
                "Photo uploaded to Firebase"
            ]
            
            found_success = []
            for indicator in success_indicators:
                for log in camera_logs:
                    if indicator in log:
                        found_success.append(indicator)
                        break
            
            # Check for error indicators
            error_indicators = [
                "CameraType",
                "undefined",
                "Cannot read properties of undefined (reading 'front')"
            ]
            
            found_errors = []
            for indicator in error_indicators:
                for log in error_logs:
                    if indicator in log:
                        found_errors.append(indicator)
            
            logger.info(f"📱 Camera logs found: {len(camera_logs)}")
            logger.info(f"✅ Success indicators: {found_success}")
            logger.info(f"❌ Error indicators: {found_errors}")
            
            return {
                'camera_logs': camera_logs,
                'success_indicators': found_success,
                'error_indicators': found_errors
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to check console logs: {e}")
            return None
    
    def verify_photo_in_gallery(self):
        """Verify photo appears in dashboard gallery"""
        try:
            logger.info("🔍 Verifying photo in gallery...")
            
            # Wait for photos to load (give time for upload)
            time.sleep(10)
            
            # Refresh the page to ensure latest data
            self.dashboard_driver.refresh()
            time.sleep(3)
            
            # Navigate back to device management if needed
            try:
                device_manage_button = WebDriverWait(self.dashboard_driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Manage')]"))
                )
                device_manage_button.click()
                time.sleep(2)
            except:
                pass
            
            # Check photo gallery
            photo_gallery = WebDriverWait(self.dashboard_driver, 10).until(
                EC.presence_of_element_located((By.ID, "photoGallery"))
            )
            
            # Look for photo elements
            photos = photo_gallery.find_elements(By.TAG_NAME, "img")
            
            if len(photos) > 0:
                logger.info(f"✅ Found {len(photos)} photos in gallery")
                
                # Check if photos have valid src
                valid_photos = 0
                for photo in photos:
                    src = photo.get_attribute('src')
                    if src and 'data:image' in src and len(src) > 100:
                        valid_photos += 1
                
                logger.info(f"✅ {valid_photos} photos have valid base64 data")
                return valid_photos > 0
            else:
                # Check for "No photos" message
                no_photos_text = photo_gallery.find_elements(By.XPATH, "//*[contains(text(), 'No photos captured yet')]")
                if no_photos_text:
                    logger.error("❌ Photo gallery shows 'No photos captured yet'")
                else:
                    logger.error("❌ Photo gallery is empty")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to verify photo in gallery: {e}")
            return False
    
    def run_comprehensive_test(self):
        """Run the complete camera functionality test"""
        logger.info("🚀 Starting Guardian Eye Camera Functionality Test")
        
        results = {
            'setup': False,
            'mobile_login': False,
            'dashboard_login': False,
            'camera_trigger': False,
            'console_logs': None,
            'photo_gallery': False,
            'overall_success': False
        }
        
        try:
            # Step 1: Setup
            logger.info("\n=== STEP 1: Setup Drivers ===")
            results['setup'] = self.setup_drivers()
            if not results['setup']:
                return results
            
            # Step 2: Mobile Login
            logger.info("\n=== STEP 2: Mobile App Login ===")
            results['mobile_login'] = self.test_mobile_login()
            
            # Step 3: Dashboard Login
            logger.info("\n=== STEP 3: Dashboard Login ===")
            results['dashboard_login'] = self.test_dashboard_login()
            
            if not results['dashboard_login']:
                return results
            
            # Step 4: Trigger Camera Capture
            logger.info("\n=== STEP 4: Trigger Camera Capture ===")
            results['camera_trigger'] = self.trigger_camera_capture()
            
            # Step 5: Check Console Logs
            logger.info("\n=== STEP 5: Check Mobile Console Logs ===")
            if results['mobile_login']:
                results['console_logs'] = self.check_mobile_console_logs()
            
            # Step 6: Verify Photo Gallery
            logger.info("\n=== STEP 6: Verify Photo in Gallery ===")
            results['photo_gallery'] = self.verify_photo_in_gallery()
            
            # Overall success
            results['overall_success'] = (
                results['setup'] and
                results['dashboard_login'] and
                results['camera_trigger'] and
                results['photo_gallery'] and
                (results['console_logs'] is not None and 
                 len(results['console_logs'].get('error_indicators', [])) == 0)
            )
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Test execution failed: {e}")
            return results
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        try:
            if self.mobile_driver:
                self.mobile_driver.quit()
            if self.dashboard_driver:
                self.dashboard_driver.quit()
            logger.info("🧹 Cleanup completed")
        except Exception as e:
            logger.error(f"❌ Cleanup error: {e}")

def main():
    """Main test execution"""
    test = CameraFunctionalityTest()
    results = test.run_comprehensive_test()
    
    # Print final results
    print("\n" + "="*60)
    print("🎯 GUARDIAN EYE CAMERA FUNCTIONALITY TEST RESULTS")
    print("="*60)
    
    print(f"✅ Setup: {'PASS' if results['setup'] else 'FAIL'}")
    print(f"✅ Mobile Login: {'PASS' if results['mobile_login'] else 'FAIL'}")
    print(f"✅ Dashboard Login: {'PASS' if results['dashboard_login'] else 'FAIL'}")
    print(f"✅ Camera Trigger: {'PASS' if results['camera_trigger'] else 'FAIL'}")
    print(f"✅ Photo Gallery: {'PASS' if results['photo_gallery'] else 'FAIL'}")
    
    if results['console_logs']:
        print(f"✅ Console Success Indicators: {len(results['console_logs']['success_indicators'])}")
        print(f"❌ Console Error Indicators: {len(results['console_logs']['error_indicators'])}")
        
        if results['console_logs']['error_indicators']:
            print("\n🚨 CRITICAL ERRORS FOUND:")
            for error in results['console_logs']['error_indicators']:
                print(f"   - {error}")
    
    print(f"\n🎯 OVERALL RESULT: {'✅ PASS' if results['overall_success'] else '❌ FAIL'}")
    
    if results['overall_success']:
        print("\n🎉 Camera functionality is working correctly!")
        print("📸 Photos are being captured and uploaded successfully")
        print("🚀 App is ready for deployment")
    else:
        print("\n⚠️  Camera functionality issues detected!")
        print("🔧 Review the errors above before deployment")
    
    print("="*60)
    
    return results['overall_success']

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)