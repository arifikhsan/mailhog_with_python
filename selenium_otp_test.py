import re
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class MailHogHelper:
    """Helper class to interact with MailHog API during Selenium tests"""
    
    def __init__(self, mailhog_url="http://localhost:8025"):
        self.api_url = f"{mailhog_url}/api/v2"
        
    def wait_for_email(self, to_email, subject_contains=None, timeout=30, poll_interval=1):
        """
        Wait for an email to arrive in MailHog
        
        Args:
            to_email: Recipient email address
            subject_contains: Optional string that should be in the subject
            timeout: Maximum time to wait in seconds
            poll_interval: How often to check for new emails
            
        Returns:
            The email message dict if found, None if timeout
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # Search for emails to the recipient
                response = requests.get(
                    f"{self.api_url}/search",
                    params={"kind": "to", "query": to_email}
                )
                response.raise_for_status()
                data = response.json()
                
                messages = data.get("items", [])
                
                # Filter by subject if provided
                if subject_contains:
                    messages = [
                        msg for msg in messages
                        if subject_contains.lower() in 
                        msg.get("Content", {}).get("Headers", {}).get("Subject", [""])[0].lower()
                    ]
                
                if messages:
                    # Return the most recent message
                    return messages[0]
                    
            except Exception as e:
                print(f"Error checking MailHog: {e}")
            
            time.sleep(poll_interval)
        
        return None
    
    def extract_otp_from_email(self, message, pattern=r'\b\d{6}\b'):
        """
        Extract OTP code from email message
        
        Args:
            message: Email message dict from MailHog
            pattern: Regex pattern to match OTP (default: 6-digit code)
            
        Returns:
            OTP code as string, or None if not found
        """
        try:
            # Get email body
            body = message.get("Content", {}).get("Body", "")
            
            # Search for OTP pattern
            match = re.search(pattern, body)
            if match:
                return match.group(0)
                
        except Exception as e:
            print(f"Error extracting OTP: {e}")
        
        return None
    
    def get_latest_email(self, to_email=None):
        """Get the most recent email, optionally filtered by recipient"""
        try:
            if to_email:
                response = requests.get(
                    f"{self.api_url}/search",
                    params={"kind": "to", "query": to_email}
                )
            else:
                response = requests.get(f"{self.api_url}/messages")
            
            response.raise_for_status()
            data = response.json()
            messages = data.get("items", [])
            
            return messages[0] if messages else None
            
        except Exception as e:
            print(f"Error getting latest email: {e}")
            return None
    
    def delete_all_messages(self):
        """Clear all messages from MailHog"""
        try:
            response = requests.delete(f"{self.api_url.replace('v2', 'v1')}/messages")
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Error deleting messages: {e}")
            return False


# Example Selenium test with OTP flow
def test_otp_login():
    # Initialize MailHog helper
    mailhog = MailHogHelper()
    
    # Clear old emails before test
    mailhog.delete_all_messages()
    
    # Initialize Selenium driver
    driver = webdriver.Chrome()
    
    try:
        # Navigate to your application
        driver.get("http://localhost:3000/login")
        
        # Enter email and request OTP
        test_email = "testuser@example.com"
        email_input = driver.find_element(By.ID, "email")
        email_input.send_keys(test_email)
        
        submit_button = driver.find_element(By.ID, "send-otp-button")
        submit_button.click()
        
        print("⏳ Waiting for OTP email...")
        
        # Wait for OTP email to arrive
        email_message = mailhog.wait_for_email(
            to_email=test_email,
            subject_contains="OTP",  # Adjust based on your email subject
            timeout=30
        )
        
        if email_message:
            print("✓ Email received!")
            
            # Extract OTP code
            otp_code = mailhog.extract_otp_from_email(email_message)
            
            if otp_code:
                print(f"✓ OTP extracted: {otp_code}")
                
                # Enter OTP in the form
                otp_input = driver.find_element(By.ID, "otp-code")
                otp_input.send_keys(otp_code)
                
                verify_button = driver.find_element(By.ID, "verify-button")
                verify_button.click()
                
                # Wait for successful login
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "dashboard"))
                )
                
                print("✓ Login successful!")
            else:
                print("✗ Could not extract OTP from email")
        else:
            print("✗ No email received within timeout")
            
    except Exception as e:
        print(f"✗ Test failed: {e}")
    finally:
        driver.quit()


if __name__ == "__main__":
    test_otp_login()
