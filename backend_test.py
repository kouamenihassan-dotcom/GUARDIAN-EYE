#!/usr/bin/env python3
"""
Guardian Eye Firebase Testing Suite
Tests Firebase authentication and real-time database functionality
"""

import requests
import json
import time
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class GuardianEyeFirebaseTest:
    def __init__(self):
        self.mobile_url = "https://device-security-hub-2.preview.emergentagent.com"
        self.dashboard_url = "https://device-security-hub-2.preview.emergentagent.com/dashboard.html"
        self.test_email = "test@guardianeye.com"
        self.test_password = "test123456"
        self.driver = None
        self.test_results = []
        
    def setup_driver(self):
        """Setup Chrome driver with appropriate options"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.binary_location = "/usr/bin/chromium"
        
        try:
            # Use chromium-driver
            from selenium.webdriver.chrome.service import Service
            service = Service("/usr/bin/chromedriver")
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.implicitly_wait(10)
            return True
        except Exception as e:
            print(f"Failed to setup Chrome/Chromium driver: {e}")
            return False
    
    def log_result(self, test_name, status, message):
        """Log test result"""
        result = {
            "test": test_name,
            "status": status,
            "message": message,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.test_results.append(result)
        print(f"[{status}] {test_name}: {message}")
    
    def test_mobile_app_accessibility(self):
        """Test if mobile app URL is accessible"""
        try:
            self.driver.get(self.mobile_url)
            time.sleep(3)
            
            # Check if page loads
            page_title = self.driver.title
            if page_title:
                self.log_result("Mobile App Accessibility", "PASS", f"Mobile app loaded successfully. Title: {page_title}")
                return True
            else:
                self.log_result("Mobile App Accessibility", "FAIL", "Mobile app page has no title")
                return False
                
        except Exception as e:
            self.log_result("Mobile App Accessibility", "FAIL", f"Failed to load mobile app: {e}")
            return False
    
    def test_mobile_app_signup_flow(self):
        """Test mobile app signup functionality"""
        try:
            self.driver.get(self.mobile_url)
            time.sleep(3)
            
            # Look for signup link/button
            signup_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Sign Up') or contains(text(), 'Create Account')]")
            
            if signup_elements:
                signup_elements[0].click()
                time.sleep(2)
                
                # Check if signup form is visible
                email_inputs = self.driver.find_elements(By.XPATH, "//input[@type='email' or @placeholder='Email']")
                password_inputs = self.driver.find_elements(By.XPATH, "//input[@type='password' or @placeholder='Password']")
                
                if email_inputs and password_inputs:
                    # Fill signup form
                    email_inputs[0].clear()
                    email_inputs[0].send_keys(self.test_email)
                    
                    password_inputs[0].clear()
                    password_inputs[0].send_keys(self.test_password)
                    
                    # If there's a confirm password field
                    if len(password_inputs) > 1:
                        password_inputs[1].clear()
                        password_inputs[1].send_keys(self.test_password)
                    
                    # Find and click signup button
                    signup_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Create Account') or contains(text(), 'Sign Up')]")
                    if signup_buttons:
                        signup_buttons[0].click()
                        time.sleep(5)
                        
                        # Check for success indicators
                        current_url = self.driver.current_url
                        page_source = self.driver.page_source.lower()
                        
                        if "home" in current_url or "dashboard" in current_url or "success" in page_source:
                            self.log_result("Mobile App Signup", "PASS", "Signup completed successfully")
                            return True
                        else:
                            self.log_result("Mobile App Signup", "FAIL", f"Signup may have failed. Current URL: {current_url}")
                            return False
                    else:
                        self.log_result("Mobile App Signup", "FAIL", "Signup button not found")
                        return False
                else:
                    self.log_result("Mobile App Signup", "FAIL", "Email or password input fields not found")
                    return False
            else:
                self.log_result("Mobile App Signup", "FAIL", "Signup link/button not found")
                return False
                
        except Exception as e:
            self.log_result("Mobile App Signup", "FAIL", f"Error during signup: {e}")
            return False
    
    def test_mobile_app_login_flow(self):
        """Test mobile app login functionality"""
        try:
            self.driver.get(self.mobile_url)
            time.sleep(3)
            
            # Look for email and password inputs
            email_inputs = self.driver.find_elements(By.XPATH, "//input[@type='email' or @placeholder='Email']")
            password_inputs = self.driver.find_elements(By.XPATH, "//input[@type='password' or @placeholder='Password']")
            
            if email_inputs and password_inputs:
                # Fill login form
                email_inputs[0].clear()
                email_inputs[0].send_keys(self.test_email)
                
                password_inputs[0].clear()
                password_inputs[0].send_keys(self.test_password)
                
                # Find and click login button
                login_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Sign In') or contains(text(), 'Login')]")
                if login_buttons:
                    login_buttons[0].click()
                    time.sleep(5)
                    
                    # Check for successful login
                    current_url = self.driver.current_url
                    page_source = self.driver.page_source.lower()
                    
                    if "home" in current_url or "guardian eye" in page_source:
                        self.log_result("Mobile App Login", "PASS", "Login completed successfully")
                        return True
                    else:
                        self.log_result("Mobile App Login", "FAIL", f"Login may have failed. Current URL: {current_url}")
                        return False
                else:
                    self.log_result("Mobile App Login", "FAIL", "Login button not found")
                    return False
            else:
                self.log_result("Mobile App Login", "FAIL", "Email or password input fields not found")
                return False
                
        except Exception as e:
            self.log_result("Mobile App Login", "FAIL", f"Error during login: {e}")
            return False
    
    def test_web_dashboard_accessibility(self):
        """Test if web dashboard URL is accessible"""
        try:
            self.driver.get(self.dashboard_url)
            time.sleep(3)
            
            # Check if dashboard page loads
            page_title = self.driver.title
            page_source = self.driver.page_source.lower()
            
            if "guardian eye" in page_source or "dashboard" in page_title.lower():
                self.log_result("Web Dashboard Accessibility", "PASS", f"Dashboard loaded successfully. Title: {page_title}")
                return True
            else:
                self.log_result("Web Dashboard Accessibility", "FAIL", f"Dashboard page may not have loaded correctly. Title: {page_title}")
                return False
                
        except Exception as e:
            self.log_result("Web Dashboard Accessibility", "FAIL", f"Failed to load dashboard: {e}")
            return False
    
    def test_web_dashboard_login(self):
        """Test web dashboard login functionality"""
        try:
            self.driver.get(self.dashboard_url)
            time.sleep(3)
            
            # Look for login form
            email_input = self.driver.find_element(By.ID, "email")
            password_input = self.driver.find_element(By.ID, "password")
            
            if email_input and password_input:
                # Fill login form
                email_input.clear()
                email_input.send_keys(self.test_email)
                
                password_input.clear()
                password_input.send_keys(self.test_password)
                
                # Submit form
                login_form = self.driver.find_element(By.ID, "loginForm")
                login_form.submit()
                time.sleep(5)
                
                # Check for successful login (dashboard should be visible)
                try:
                    dashboard_element = self.driver.find_element(By.ID, "dashboard")
                    if dashboard_element.is_displayed():
                        self.log_result("Web Dashboard Login", "PASS", "Dashboard login successful")
                        return True
                    else:
                        self.log_result("Web Dashboard Login", "FAIL", "Dashboard not visible after login")
                        return False
                except NoSuchElementException:
                    self.log_result("Web Dashboard Login", "FAIL", "Dashboard element not found after login")
                    return False
            else:
                self.log_result("Web Dashboard Login", "FAIL", "Login form elements not found")
                return False
                
        except Exception as e:
            self.log_result("Web Dashboard Login", "FAIL", f"Error during dashboard login: {e}")
            return False
    
    def test_device_registration(self):
        """Test if device appears in dashboard after mobile login"""
        try:
            # First ensure we're logged into dashboard
            self.driver.get(self.dashboard_url)
            time.sleep(3)
            
            # Login to dashboard
            email_input = self.driver.find_element(By.ID, "email")
            password_input = self.driver.find_element(By.ID, "password")
            
            email_input.clear()
            email_input.send_keys(self.test_email)
            password_input.clear()
            password_input.send_keys(self.test_password)
            
            login_form = self.driver.find_element(By.ID, "loginForm")
            login_form.submit()
            time.sleep(5)
            
            # Check for device list
            device_container = self.driver.find_element(By.ID, "deviceListContainer")
            device_content = device_container.text.lower()
            
            if "no devices" in device_content or "loading" in device_content:
                self.log_result("Device Registration", "FAIL", "No devices found in dashboard")
                return False
            else:
                self.log_result("Device Registration", "PASS", "Device(s) found in dashboard")
                return True
                
        except Exception as e:
            self.log_result("Device Registration", "FAIL", f"Error checking device registration: {e}")
            return False
    
    def test_device_status_controls(self):
        """Test device status control buttons"""
        try:
            # Ensure we're in dashboard
            self.driver.get(self.dashboard_url)
            time.sleep(3)
            
            # Login if needed
            try:
                email_input = self.driver.find_element(By.ID, "email")
                password_input = self.driver.find_element(By.ID, "password")
                
                email_input.clear()
                email_input.send_keys(self.test_email)
                password_input.clear()
                password_input.send_keys(self.test_password)
                
                login_form = self.driver.find_element(By.ID, "loginForm")
                login_form.submit()
                time.sleep(5)
            except:
                pass  # Already logged in
            
            # Look for manage button
            manage_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Manage')]")
            if manage_buttons:
                manage_buttons[0].click()
                time.sleep(2)
                
                # Check if control panel is visible
                control_panel = self.driver.find_element(By.ID, "controlPanel")
                if control_panel.is_displayed():
                    # Test Mark as Stolen button
                    stolen_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Mark as Stolen')]")
                    if stolen_buttons:
                        self.log_result("Device Status Controls", "PASS", "Device control buttons are accessible")
                        return True
                    else:
                        self.log_result("Device Status Controls", "FAIL", "Control buttons not found")
                        return False
                else:
                    self.log_result("Device Status Controls", "FAIL", "Control panel not visible")
                    return False
            else:
                self.log_result("Device Status Controls", "FAIL", "No manage buttons found")
                return False
                
        except Exception as e:
            self.log_result("Device Status Controls", "FAIL", f"Error testing device controls: {e}")
            return False
    
    def run_all_tests(self):
        """Run all Firebase tests"""
        print("Starting Guardian Eye Firebase Testing Suite...")
        print("=" * 60)
        
        if not self.setup_driver():
            print("Failed to setup test environment")
            return False
        
        try:
            # Test mobile app
            self.test_mobile_app_accessibility()
            self.test_mobile_app_signup_flow()
            self.test_mobile_app_login_flow()
            
            # Test web dashboard
            self.test_web_dashboard_accessibility()
            self.test_web_dashboard_login()
            
            # Test device functionality
            self.test_device_registration()
            self.test_device_status_controls()
            
        finally:
            if self.driver:
                self.driver.quit()
        
        # Print summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result["status"] == "PASS")
        failed = sum(1 for result in self.test_results if result["status"] == "FAIL")
        
        print(f"Total Tests: {len(self.test_results)}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        
        if failed > 0:
            print("\nFAILED TESTS:")
            for result in self.test_results:
                if result["status"] == "FAIL":
                    print(f"- {result['test']}: {result['message']}")
        
        return failed == 0

if __name__ == "__main__":
    tester = GuardianEyeFirebaseTest()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)