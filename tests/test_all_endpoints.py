#!/usr/bin/env python3
"""
Comprehensive test suite for secure authentication system
Tests the 6 core endpoints: /, /register, /login, /token/refresh, /logout, /users/me
"""
import requests
import pyotp
from datetime import datetime

BASE_URL = "http://localhost:8000"

# ANSI color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def print_test(title):
    print(f"\n{BLUE}{'='*60}")
    print(f"TEST: {title}")
    print(f"{'='*60}{RESET}")

def print_success(msg):
    print(f"{GREEN}[PASS] {msg}{RESET}")

def print_error(msg):
    print(f"{RED}[FAIL] {msg}{RESET}")

def print_info(msg):
    print(f"{YELLOW}[INFO] {msg}{RESET}")

def test_health_check():
    """Test GET /"""
    print_test("Health Check")
    
    try:
        r = requests.get(f"{BASE_URL}/")
        if r.status_code == 200:
            result = r.json()
            print_success(f"Health check successful: {result.get('message', 'OK')}")
            print(f"  Status: {result.get('status', 'N/A')}")
            print(f"  Version: {result.get('version', 'N/A')}")
            return True
        else:
            print_error(f"Health check failed: {r.status_code}")
            return False
    except Exception as e:
        print_error(f"Health check error: {str(e)}")
        return False

def test_user_registration():
    """Test POST /register"""
    print_test("User Registration")
    
    payload = {
        "username": "testuser_" + str(int(datetime.now().timestamp() % 10000)),
        "email": "test@example.com",
        "password": "SecureP@ss123!"
    }
    
    try:
        r = requests.post(f"{BASE_URL}/register", json=payload)
        if r.status_code in [200, 201]:
            result = r.json()
            print_success(f"Registration successful: {result.get('msg', 'OK')}")
            print(f"  Username: {result.get('username')}")
            print(f"  Email: {result.get('email')}")
            print(f"  TOTP Secret: {result.get('totp_secret', 'N/A')}")
            return result
        else:
            print_error(f"Registration failed: {r.status_code}")
            print(f"  Response: {r.text}")
            return None
    except Exception as e:
        print_error(f"Registration error: {str(e)}")
        return None

def test_user_login(username, password, totp_secret):
    """Test POST /login"""
    print_test("User Login")
    
    # Generate valid TOTP code
    totp = pyotp.TOTP(totp_secret)
    totp_code = totp.now()
    
    payload = {
        "username": username,
        "password": password,
        "totp": totp_code
    }
    
    try:
        r = requests.post(f"{BASE_URL}/login", json=payload)
        if r.status_code == 200:
            result = r.json()
            print_success("Login successful")
            print(f"  Access Token (first 50 chars): {result.get('access_token', '')[:50]}...")
            print(f"  Refresh Token (first 50 chars): {result.get('refresh_token', '')[:50]}...")
            print(f"  Token Type: {result.get('token_type')}")
            return result
        else:
            print_error(f"Login failed: {r.status_code}")
            print(f"  Response: {r.text}")
            return None
    except Exception as e:
        print_error(f"Login error: {str(e)}")
        return None

def test_token_refresh(refresh_token):
    """Test POST /token/refresh"""
    print_test("Token Refresh")
    
    payload = {
        "refresh_token": refresh_token
    }
    
    try:
        r = requests.post(f"{BASE_URL}/token/refresh", json=payload)
        if r.status_code == 200:
            result = r.json()
            print_success("Token refresh successful")
            print(f"  New Access Token (first 50 chars): {result.get('access_token', '')[:50]}...")
            print(f"  Token Type: {result.get('token_type')}")
            return result.get('access_token')
        else:
            print_error(f"Token refresh failed: {r.status_code}")
            print(f"  Response: {r.text}")
            return None
    except Exception as e:
        print_error(f"Token refresh error: {str(e)}")
        return None

def test_get_current_user(access_token):
    """Test GET /users/me"""
    print_test("Get Current User Profile")
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    try:
        r = requests.get(f"{BASE_URL}/users/me", headers=headers)
        if r.status_code == 200:
            result = r.json()
            print_success("Retrieved user profile")
            print(f"  ID: {result.get('id')}")
            print(f"  Username: {result.get('username')}")
            print(f"  Email: {result.get('email')}")
            print(f"  TOTP Enabled: {result.get('totp_enabled')}")
            print(f"  Created At: {result.get('created_at')}")
            return result
        else:
            print_error(f"Get user profile failed: {r.status_code}")
            print(f"  Response: {r.text}")
            return None
    except Exception as e:
        print_error(f"Get user profile error: {str(e)}")
        return None

def test_logout(refresh_token):
    """Test POST /logout"""
    print_test("User Logout")
    
    payload = {
        "refresh_token": refresh_token
    }
    
    try:
        r = requests.post(f"{BASE_URL}/logout", json=payload)
        if r.status_code == 200:
            result = r.json()
            print_success(f"Logout successful: {result.get('msg')}")
            return True
        else:
            print_error(f"Logout failed: {r.status_code}")
            print(f"  Response: {r.text}")
            return False
    except Exception as e:
        print_error(f"Logout error: {str(e)}")
        return False

def test_invalid_credentials():
    """Test login with invalid credentials"""
    print_test("Invalid Credentials (Security Test)")
    
    payload = {
        "username": "nonexistent_user",
        "password": "WrongPassword123!",
        "totp": "000000"
    }
    
    try:
        r = requests.post(f"{BASE_URL}/login", json=payload)
        if r.status_code == 401:
            print_success(f"Invalid credentials correctly rejected: {r.status_code}")
            print(f"  Detail: {r.json().get('detail')}")
            return True
        else:
            print_error(f"Expected 401, got {r.status_code}")
            return False
    except Exception as e:
        print_error(f"Test error: {str(e)}")
        return False

def test_unauthorized_access():
    """Test accessing protected endpoint without token"""
    print_test("Unauthorized Access (Security Test)")
    
    try:
        r = requests.get(f"{BASE_URL}/users/me")
        if r.status_code == 401:
            print_success(f"Unauthorized access correctly blocked: {r.status_code}")
            print(f"  Detail: {r.json().get('detail')}")
            return True
        else:
            print_error(f"Expected 401, got {r.status_code}")
            return False
    except Exception as e:
        print_error(f"Test error: {str(e)}")
        return False

def test_invalid_token():
    """Test accessing protected endpoint with invalid token"""
    print_test("Invalid Token (Security Test)")
    
    headers = {
        "Authorization": "Bearer invalid_token_12345"
    }
    
    try:
        r = requests.get(f"{BASE_URL}/users/me", headers=headers)
        if r.status_code == 401:
            print_success(f"Invalid token correctly rejected: {r.status_code}")
            print(f"  Detail: {r.json().get('detail')}")
            return True
        else:
            print_error(f"Expected 401, got {r.status_code}")
            return False
    except Exception as e:
        print_error(f"Test error: {str(e)}")
        return False

def test_weak_password():
    """Test registration with weak password"""
    print_test("Weak Password Validation")
    
    payload = {
        "username": f"test_{int(datetime.now().timestamp() % 10000)}",
        "email": "weak@example.com",
        "password": "weak"
    }
    
    try:
        r = requests.post(f"{BASE_URL}/register", json=payload)
        if r.status_code == 422:
            print_success(f"Weak password correctly rejected: {r.status_code}")
            return True
        else:
            print_error(f"Weak password was accepted (should be rejected): {r.status_code}")
            return False
    except Exception as e:
        print_error(f"Test error: {str(e)}")
        return False

def test_invalid_email():
    """Test registration with invalid email"""
    print_test("Email Validation")
    
    payload = {
        "username": f"test_{int(datetime.now().timestamp() % 10000)}",
        "email": "invalid-email",
        "password": "SecureP@ss123!"
    }
    
    try:
        r = requests.post(f"{BASE_URL}/register", json=payload)
        if r.status_code in [400, 422]:
            print_success(f"Invalid email correctly rejected: {r.status_code}")
            return True
        else:
            print_error(f"Invalid email was accepted (should be rejected): {r.status_code}")
            return False
    except Exception as e:
        print_error(f"Test error: {str(e)}")
        return False

def main():
    """Run all tests"""
    print(f"\n{BLUE}{'='*60}")
    print("SECURE AUTHENTICATION SYSTEM - TEST SUITE")
    print("Testing Core 6 Endpoints")
    print(f"{'='*60}{RESET}\n")
    
    test_results = []
    
    # Test 1: Health Check
    print_info("Test 1/12: Health Check")
    result = test_health_check()
    test_results.append(("Health Check", result))
    
    # Test 2: Registration
    print_info("\nTest 2/12: User Registration")
    reg_result = test_user_registration()
    if reg_result:
        test_results.append(("User Registration", True))
        username = reg_result.get('username')
        totp_secret = reg_result.get('totp_secret')
        password = "SecureP@ss123!"
    else:
        test_results.append(("User Registration", False))
        print_error("Cannot continue tests without registration")
        print_summary(test_results)
        return
    
    # Test 3: Login
    print_info("\nTest 3/12: User Login")
    login_result = test_user_login(username, password, totp_secret)
    if login_result:
        test_results.append(("User Login", True))
        access_token = login_result.get('access_token')
        refresh_token = login_result.get('refresh_token')
    else:
        test_results.append(("User Login", False))
        print_error("Cannot continue tests without login")
        print_summary(test_results)
        return
    
    # Test 4: Get Current User Profile
    print_info("\nTest 4/12: Get User Profile")
    profile_result = test_get_current_user(access_token)
    test_results.append(("Get User Profile", profile_result is not None))
    
    # Test 5: Token Refresh
    print_info("\nTest 5/12: Token Refresh")
    new_access_token = test_token_refresh(refresh_token)
    test_results.append(("Token Refresh", new_access_token is not None))
    if new_access_token:
        access_token = new_access_token  # Use new token
    
    # Test 6: Logout
    print_info("\nTest 6/12: User Logout")
    logout_result = test_logout(refresh_token)
    test_results.append(("User Logout", logout_result))
    
    # Security Tests
    print_info("\nSecurity Tests")
    
    # Test 7: Invalid Credentials
    print_info("\nTest 7/12: Invalid Credentials")
    result = test_invalid_credentials()
    test_results.append(("Invalid Credentials", result))
    
    # Test 8: Unauthorized Access
    print_info("\nTest 8/12: Unauthorized Access")
    result = test_unauthorized_access()
    test_results.append(("Unauthorized Access", result))
    
    # Test 9: Invalid Token
    print_info("\nTest 9/12: Invalid Token")
    result = test_invalid_token()
    test_results.append(("Invalid Token", result))
    
    # Validation Tests
    print_info("\nValidation Tests")
    
    # Test 10: Weak Password
    print_info("\nTest 10/12: Weak Password Validation")
    result = test_weak_password()
    test_results.append(("Weak Password Validation", result))
    
    # Test 11: Invalid Email
    print_info("\nTest 11/12: Email Validation")
    result = test_invalid_email()
    test_results.append(("Email Validation", result))
    
    # Test 12: Try to use refresh token after logout (should fail)
    print_info("\nTest 12/12: Token Invalidation")
    print_test("Refresh Token After Logout (Security Test)")
    try:
        r = requests.post(f"{BASE_URL}/token/refresh", json={"refresh_token": refresh_token})
        if r.status_code == 401:
            print_success(f"Refresh token correctly invalidated after logout: {r.status_code}")
            test_results.append(("Token Invalidation", True))
        else:
            print_error(f"Refresh token still valid after logout: {r.status_code}")
            test_results.append(("Token Invalidation", False))
    except Exception as e:
        print_error(f"Test error: {str(e)}")
        test_results.append(("Token Invalidation", False))
    
    # Print Summary
    print_summary(test_results)

def print_summary(test_results):
    """Print test summary"""
    print(f"\n{BLUE}{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}{RESET}")
    
    passed = sum(1 for _, result in test_results if result)
    failed = sum(1 for _, result in test_results if not result)
    
    for test_name, result in test_results:
        if result:
            print_success(f"{test_name}: PASS")
        else:
            print_error(f"{test_name}: FAIL")
    
    print(f"\n{BLUE}Total: {passed} passed, {failed} failed out of {len(test_results)} tests{RESET}")
    
    if failed == 0:
        print(f"{GREEN}✓ All tests passed!{RESET}\n")
    else:
        print(f"{RED}✗ {failed} test(s) failed{RESET}\n")

if __name__ == "__main__":
    main()
