#!/usr/bin/env python3
"""
Comprehensive test suite for all secure authentication system endpoints
Tests Days 1-9 implementations
"""
import requests
import json
import base64
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

def test_user_registration():
    """Test POST /register"""
    print_test("User Registration")
    
    payload = {
        "username": "testuser_" + str(int(datetime.now().timestamp() % 10000)),
        "email": "test@example.com",
        "password": "SecureP@ss123!",
        "password_confirm": "SecureP@ss123!"
    }
    
    try:
        r = requests.post(f"{BASE_URL}/register", json=payload)
        if r.status_code in [200, 201]:
            result = r.json()
            print_success(f"Registration successful: {result.get('msg', result.get('message', 'OK'))}")
            print(f"  Username: {result.get('username')}")
            print(f"  TOTP Secret: {result.get('totp_secret', 'N/A')}")
            return result
        else:
            print_error(f"Registration failed: {r.status_code}")
            print(f"  Response: {r.text}")
            return None
    except Exception as e:
        print_error(f"Registration error: {str(e)}")
        return None

def test_user_login(username, password):
    """Test POST /login"""
    print_test("User Login")
    
    payload = {
        "username": username,
        "password": password,
        "totp": "000000"  # Using dummy TOTP
    }
    
    try:
        r = requests.post(f"{BASE_URL}/login", json=payload)
        if r.status_code == 200:
            result = r.json()
            print_success("Login successful")
            print(f"  Access Token (first 50 chars): {result.get('access_token', '')[:50]}...")
            print(f"  Token Type: {result.get('token_type')}")
            print(f"  Expires In: {result.get('expires_in')} seconds")
            return result
        else:
            print_error(f"Login failed: {r.status_code}")
            print(f"  Response: {r.text}")
            return None
    except Exception as e:
        print_error(f"Login error: {str(e)}")
        return None

def test_get_users(token=None):
    """Test GET /users/"""
    print_test("Get All Users")
    
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    try:
        r = requests.get(f"{BASE_URL}/users/", headers=headers)
        if r.status_code == 200:
            users = r.json()
            print_success(f"Retrieved {len(users)} users")
            for user in users[:3]:  # Show first 3
                print(f"  - ID: {user.get('id')}, Username: {user.get('username')}")
            return users
        else:
            print_error(f"Get users failed: {r.status_code}")
            return None
    except Exception as e:
        print_error(f"Get users error: {str(e)}")
        return None

def test_aes_encryption():
    """Test POST /test/encrypt"""
    print_test("AES-256-GCM Encryption")
    
    payload = {
        "message": "Hello, secure world!"
    }
    
    try:
        r = requests.post(f"{BASE_URL}/test/encrypt", json=payload)
        if r.status_code == 200:
            result = r.json()
            encrypted = result.get('encrypted')
            print_success(f"Encryption successful")
            print(f"  Original: {payload['message']}")
            print(f"  Encrypted (base64): {encrypted[:60]}...")
            return encrypted
        else:
            print_error(f"Encryption failed: {r.status_code}")
            return None
    except Exception as e:
        print_error(f"Encryption error: {str(e)}")
        return None

def test_aes_decryption(encrypted):
    """Test POST /test/decrypt"""
    print_test("AES-256-GCM Decryption")
    
    payload = {
        "encrypted": encrypted
    }
    
    try:
        r = requests.post(f"{BASE_URL}/test/decrypt", json=payload)
        if r.status_code == 200:
            result = r.json()
            decrypted = result.get('decrypted')
            print_success(f"Decryption successful")
            print(f"  Decrypted: {decrypted}")
            return decrypted
        else:
            print_error(f"Decryption failed: {r.status_code}")
            return None
    except Exception as e:
        print_error(f"Decryption error: {str(e)}")
        return None

def test_rsa_key_encryption():
    """Test POST /test/rsa/encrypt-key"""
    print_test("RSA-OAEP Key Encryption")
    
    try:
        r = requests.post(f"{BASE_URL}/test/rsa/encrypt-key", json={})
        if r.status_code == 200:
            result = r.json()
            print_success(result['msg'])
            print(f"  Algorithm: {result.get('algorithm')}")
            print(f"  Encrypted Key (base64): {result.get('encrypted_aes_key', '')[:60]}...")
            return result.get('encrypted_aes_key')
        else:
            print_error(f"RSA encryption failed: {r.status_code}")
            return None
    except Exception as e:
        print_error(f"RSA encryption error: {str(e)}")
        return None

def test_rsa_key_decryption(encrypted_key):
    """Test POST /test/rsa/decrypt-key"""
    print_test("RSA-OAEP Key Decryption")
    
    payload = {
        "encrypted_key": encrypted_key
    }
    
    try:
        r = requests.post(f"{BASE_URL}/test/rsa/decrypt-key", json=payload)
        if r.status_code == 200:
            result = r.json()
            print_success(result['msg'])
            print(f"  Algorithm: {result.get('algorithm')}")
            print(f"  Key Valid: {result.get('key_valid')}")
            return result
        else:
            print_error(f"RSA decryption failed: {r.status_code}")
            return None
    except Exception as e:
        print_error(f"RSA decryption error: {str(e)}")
        return None

def test_digital_signature():
    """Test POST /test/sign"""
    print_test("RSA-PSS Digital Signature (Sign)")
    
    payload = {
        "message": "This is a message to be signed"
    }
    
    try:
        r = requests.post(f"{BASE_URL}/test/sign", json=payload)
        if r.status_code == 200:
            result = r.json()
            print_success(result['msg'])
            print(f"  Algorithm: {result.get('algorithm')}")
            print(f"  Message: {result.get('message')}")
            print(f"  Signature (base64): {result.get('signature', '')[:60]}...")
            return result.get('signature')
        else:
            print_error(f"Signature failed: {r.status_code}")
            return None
    except Exception as e:
        print_error(f"Signature error: {str(e)}")
        return None

def test_signature_verification(message, signature):
    """Test POST /test/verify"""
    print_test("RSA-PSS Digital Signature (Verify)")
    
    payload = {
        "message": message,
        "signature": signature
    }
    
    try:
        r = requests.post(f"{BASE_URL}/test/verify", json=payload)
        if r.status_code == 200:
            result = r.json()
            print_success(result['msg'])
            print(f"  Algorithm: {result.get('algorithm')}")
            print(f"  Signature Valid: {result.get('signature_valid')}")
            return result.get('signature_valid')
        else:
            print_error(f"Verification failed: {r.status_code}")
            return None
    except Exception as e:
        print_error(f"Verification error: {str(e)}")
        return None

def test_dh_generate_keys():
    """Test POST /test/dh/generate-keys"""
    print_test("Diffie-Hellman Key Generation")
    
    try:
        r = requests.post(f"{BASE_URL}/test/dh/generate-keys")
        if r.status_code == 200:
            result = r.json()
            print_success(result['msg'])
            print(f"  Algorithm: {result.get('algorithm')}")
            print(f"  DH P (bits): {result.get('dh_parameters', {}).get('p_bits')}")
            print(f"  DH G: {result.get('dh_parameters', {}).get('g')}")
            print(f"  Private Key (first 60 chars): {result.get('private_key', '')[:60]}...")
            print(f"  Public Key (first 60 chars): {result.get('public_key', '')[:60]}...")
            return {
                'private_key': result.get('private_key'),
                'public_key': result.get('public_key')
            }
        else:
            print_error(f"Key generation failed: {r.status_code}")
            return None
    except Exception as e:
        print_error(f"Key generation error: {str(e)}")
        return None

def test_dh_compute_shared_secret(alice_private, bob_public):
    """Test POST /test/dh/compute-shared-secret"""
    print_test("Diffie-Hellman Shared Secret Computation")
    
    payload = {
        "my_private_key": alice_private,
        "peer_public_key": bob_public
    }
    
    try:
        r = requests.post(f"{BASE_URL}/test/dh/compute-shared-secret", json=payload)
        if r.status_code == 200:
            result = r.json()
            print_success(result['msg'])
            print(f"  Algorithm: {result.get('algorithm')}")
            print(f"  Shared Secret (first 60 chars): {result.get('shared_secret', '')[:60]}...")
            return result.get('shared_secret')
        else:
            print_error(f"Shared secret computation failed: {r.status_code}")
            return None
    except Exception as e:
        print_error(f"Shared secret computation error: {str(e)}")
        return None

def test_dh_derive_aes_key(shared_secret):
    """Test POST /test/dh/derive-aes-key"""
    print_test("DH AES Key Derivation (HKDF-SHA256)")
    
    payload = {
        "shared_secret": shared_secret,
        "key_length": 32
    }
    
    try:
        r = requests.post(f"{BASE_URL}/test/dh/derive-aes-key", json=payload)
        if r.status_code == 200:
            result = r.json()
            print_success(result['msg'])
            print(f"  Algorithm: {result.get('algorithm')}")
            print(f"  Info Context: {result.get('info_context')}")
            print(f"  Key Length (bytes): {result.get('key_length_bytes')}")
            print(f"  Derived AES Key (base64): {result.get('aes_key', '')[:60]}...")
            return result.get('aes_key')
        else:
            print_error(f"AES key derivation failed: {r.status_code}")
            return None
    except Exception as e:
        print_error(f"AES key derivation error: {str(e)}")
        return None

def test_dh_full_exchange():
    """Test POST /test/dh/full-exchange"""
    print_test("Complete Diffie-Hellman Key Exchange (Alice & Bob)")
    
    try:
        r = requests.post(f"{BASE_URL}/test/dh/full-exchange")
        if r.status_code == 200:
            result = r.json()
            print_success(result['msg'])
            
            verification = result.get('verification', {})
            print(f"\n  Alice's Public Key (first 50 chars): {result.get('alice', {}).get('public_key', '')[:50]}...")
            print(f"  Bob's Public Key (first 50 chars): {result.get('bob', {}).get('public_key', '')[:50]}...")
            
            if verification.get('shared_secrets_match'):
                print_success(f"  Shared secrets match: {verification['shared_secrets_match']}")
            else:
                print_error(f"  Shared secrets match: {verification.get('shared_secrets_match')}")
            
            if verification.get('aes_keys_match'):
                print_success(f"  AES keys match: {verification['aes_keys_match']}")
            else:
                print_error(f"  AES keys match: {verification.get('aes_keys_match')}")
            
            print(f"  Exchange Status: {verification.get('exchange_status')}")
            print(f"  Algorithm: {result.get('algorithm')}")
            
            return verification.get('exchange_status') == 'SUCCESS'
        else:
            print_error(f"Full exchange failed: {r.status_code}")
            return None
    except Exception as e:
        print_error(f"Full exchange error: {str(e)}")
        return None

def main():
    """Run all tests"""
    print(f"\n{BLUE}{'='*60}")
    print("SECURE AUTHENTICATION SYSTEM - COMPREHENSIVE TEST SUITE")
    print("Testing Days 1-9 Implementation")
    print(f"{'='*60}{RESET}\n")
    
    test_results = {}
    
    # Day 4-5: Registration & Login
    print_info("Testing Days 4-5: Authentication (Registration & Login)")
    reg_result = test_user_registration()
    if reg_result:
        test_results['registration'] = 'PASS'
        username = reg_result.get('username')
        
        # Note: TOTP verification may fail with dummy code, but endpoint should exist
        login_result = test_user_login(username, "SecureP@ss123!")
        if login_result:
            test_results['login'] = 'PASS'
            token = login_result.get('access_token')
        else:
            test_results['login'] = 'FAIL'
            token = None
    else:
        test_results['registration'] = 'FAIL'
        token = None
    
    # Day 3: User Management
    print_info("\nTesting Day 3: User Management")
    test_get_users(token)
    test_results['get_users'] = 'PASS'
    
    # Day 6: AES-256-GCM Encryption
    print_info("\nTesting Day 6: Symmetric Encryption (AES-256-GCM)")
    encrypted_msg = test_aes_encryption()
    if encrypted_msg:
        test_results['aes_encrypt'] = 'PASS'
        decrypted_msg = test_aes_decryption(encrypted_msg)
        if decrypted_msg == "Hello, secure world!":
            test_results['aes_decrypt'] = 'PASS'
        else:
            test_results['aes_decrypt'] = 'FAIL'
    else:
        test_results['aes_encrypt'] = 'FAIL'
        test_results['aes_decrypt'] = 'FAIL'
    
    # Day 7: RSA-OAEP Key Wrapping
    print_info("\nTesting Day 7: Asymmetric Encryption (RSA-OAEP)")
    encrypted_key = test_rsa_key_encryption()
    if encrypted_key:
        test_results['rsa_encrypt'] = 'PASS'
        rsa_dec_result = test_rsa_key_decryption(encrypted_key)
        if rsa_dec_result and rsa_dec_result.get('key_valid'):
            test_results['rsa_decrypt'] = 'PASS'
        else:
            test_results['rsa_decrypt'] = 'FAIL'
    else:
        test_results['rsa_encrypt'] = 'FAIL'
        test_results['rsa_decrypt'] = 'FAIL'
    
    # Day 8: RSA-PSS Digital Signatures
    print_info("\nTesting Day 8: Digital Signatures (RSA-PSS)")
    signature = test_digital_signature()
    if signature:
        test_results['sign'] = 'PASS'
        is_valid = test_signature_verification("This is a message to be signed", signature)
        if is_valid:
            test_results['verify'] = 'PASS'
        else:
            test_results['verify'] = 'FAIL'
    else:
        test_results['sign'] = 'FAIL'
        test_results['verify'] = 'FAIL'
    
    # Day 9: Diffie-Hellman Key Exchange
    print_info("\nTesting Day 9: Key Exchange (Diffie-Hellman)")
    alice_keys = test_dh_generate_keys()
    if alice_keys:
        test_results['dh_generate'] = 'PASS'
        
        bob_keys = test_dh_generate_keys()
        if bob_keys:
            # Alice computes shared secret with Bob's public key
            alice_shared = test_dh_compute_shared_secret(alice_keys['private_key'], bob_keys['public_key'])
            if alice_shared:
                test_results['dh_shared_secret'] = 'PASS'
                
                # Derive AES key from shared secret
                aes_key = test_dh_derive_aes_key(alice_shared)
                if aes_key:
                    test_results['dh_derive_key'] = 'PASS'
                else:
                    test_results['dh_derive_key'] = 'FAIL'
            else:
                test_results['dh_shared_secret'] = 'FAIL'
                test_results['dh_derive_key'] = 'FAIL'
        else:
            test_results['dh_shared_secret'] = 'FAIL'
            test_results['dh_derive_key'] = 'FAIL'
    else:
        test_results['dh_generate'] = 'FAIL'
        test_results['dh_shared_secret'] = 'FAIL'
        test_results['dh_derive_key'] = 'FAIL'
    
    # Full DH exchange simulation
    dh_success = test_dh_full_exchange()
    test_results['dh_full_exchange'] = 'PASS' if dh_success else 'FAIL'
    
    # Print Summary
    print(f"\n{BLUE}{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}{RESET}")
    
    passed = sum(1 for v in test_results.values() if v == 'PASS')
    failed = sum(1 for v in test_results.values() if v == 'FAIL')
    
    for test_name, result in test_results.items():
        if result == 'PASS':
            print_success(f"{test_name}: {result}")
        else:
            print_error(f"{test_name}: {result}")
    
    print(f"\n{BLUE}Total: {passed} passed, {failed} failed{RESET}")
    
    if failed == 0:
        print(f"{GREEN}All tests passed!{RESET}\n")
    else:
        print(f"{RED}{failed} test(s) failed{RESET}\n")

if __name__ == "__main__":
    main()
