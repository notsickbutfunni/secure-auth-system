# Secure Authentication System - API Reference

Base URL: `http://localhost:8000`

**Interactive Documentation:** Visit `/docs` for Swagger UI with try-it-out functionality

---

## Table of Contents
1. [Authentication Endpoints](#authentication-endpoints)
2. [Token Management](#token-management)
3. [User Profile](#user-profile)
4. [Security Features](#security-features)
5. [Error Responses](#error-responses)
6. [Testing Guide](#testing-guide)

---

## Authentication Endpoints

### 1. Health Check
**GET** `/`

**Description:** Check API status

**Response (200):**
```json
{
  "message": "Secure Authentication System API",
  "version": "1.0",
  "status": "running"
}
```

---

### 2. User Registration
**POST** `/register`

**Description:** Create a new user account with TOTP 2FA setup

**Request Body:**
```json
{
  "username": "myuser",
  "email": "user@example.com",
  "password": "SecureP@ss123!"
}
```

**Response (201/200):**
```json
{
  "msg": "User registered successfully",
  "username": "myuser",
  "email": "user@example.com",
  "totp_secret": "RJCD6YAN2KIUFW7DV56FPPWDYDAZ3CKO"
}
```

**Password Requirements:**
- Minimum 8 characters
- At least one uppercase letter (A-Z)
- At least one lowercase letter (a-z)
- At least one digit (0-9)
- At least one special character (!@#$%^&* etc.)

**Email Requirements:**
- Valid email format with @ and domain
- Less than 254 characters

**TOTP Secret:**
- Save this secret securely
- Use it with an authenticator app (Google Authenticator, Microsoft Authenticator, Authy, etc.)
- Generate 6-digit codes for login

**Error Responses:**
- `409 Conflict` - Username already exists
- `400 Bad Request` - Invalid email format
- `422 Unprocessable Entity` - Password doesn't meet requirements

---

### 3. User Login
**POST** `/login`

**Description:** Authenticate user and receive JWT tokens

**Request Body:**
```json
{
  "username": "myuser",
  "password": "SecureP@ss123!",
  "totp": "123456"
}
```

**Response (200):**
```json
{
  "msg": "Login successful",
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJteXVzZXIiLCJ0eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzMzMDEyMzQ1fQ...",
  "refresh_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJteXVzZXIiLCJ0eXBlIjoicmVmcmVzaCIsImV4cCI6MTczMzYxNzE0NX0...",
  "token_type": "bearer"
}
```

**Token Details:**
- `access_token` - Use for protected endpoints (expires in 15 minutes)
- `refresh_token` - Use to get new access token (expires in 7 days)
- `token_type` - Always "bearer"

**TOTP Code:**
- Must be valid 6-digit code from authenticator app
- Valid for 30 seconds
- Accepted with ±1 time window (90 seconds total) for clock drift tolerance

**Error Responses:**
- `401 Unauthorized` - Invalid username/password or TOTP code
- `400 Bad Request` - TOTP not configured for user

---

## Token Management

### 4. Refresh Access Token
**POST** `/token/refresh`

**Description:** Get new access token using refresh token

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJteXVzZXIiLCJ0eXBlIjoicmVmcmVzaCIsImV4cCI6MTczMzYxNzE0NX0..."
}
```

**Response (200):**
```json
{
  "msg": "Token refreshed successfully",
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJteXVzZXIiLCJ0eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzMzMDEyNjQ1fQ...",
  "token_type": "bearer"
}
```

**Error Responses:**
- `401 Unauthorized` - Refresh token expired or invalid
- `404 Not Found` - User not found
- `400 Bad Request` - Invalid token type

---

### 5. User Logout
**POST** `/logout`

**Description:** Invalidate refresh token and logout user

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJteXVzZXIiLCJ0eXBlIjoicmVmcmVzaCIsImV4cCI6MTczMzYxNzE0NX0..."
}
```

**Response (200):**
```json
{
  "msg": "Logged out successfully"
}
```

**Side Effects:**
- All refresh tokens for user are invalidated
- Existing access tokens remain valid until expiration (15 min)
- User must login again to get new tokens

**Error Responses:**
- `404 Not Found` - User not found
- `400 Bad Request` - Invalid refresh token

---

## User Profile

### 6. Get Current User
**GET** `/users/me`

**Description:** Retrieve authenticated user profile

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "id": 1,
  "username": "myuser",
  "email": "user@example.com",
  "created_at": "2025-12-05T13:49:10.622874",
  "totp_enabled": true
}
```

**Error Responses:**
- `401 Unauthorized` - Missing or invalid access token
- `404 Not Found` - User not found

---

## Security Features

### JWT Authentication (RS256)
- **Algorithm:** RSA Signature with SHA-256
- **Key Size:** 2048-bit RSA keys
- **Access Token Lifetime:** 15 minutes
- **Refresh Token Lifetime:** 7 days
- **Token Storage:** Refresh tokens encrypted with AES-256-GCM

### Password Security
- **Hashing Algorithm:** Argon2id
- **Time Cost:** Configurable (resistant to GPU attacks)
- **Memory Cost:** Configurable

### Two-Factor Authentication (2FA)
- **Method:** Time-based One-Time Password (TOTP)
- **Algorithm:** HMAC-SHA1
- **Code Length:** 6 digits
- **Time Step:** 30 seconds
- **Acceptance Window:** ±1 time step (90 seconds)

### Data Encryption
- **Refresh Token Encryption:** AES-256-GCM
- **Nonce Size:** 12 bytes (random)
- **Authentication Data:** Username

### HTTPS Recommendation
For production, always use HTTPS to protect tokens in transit.

---

## Error Responses

### 400 Bad Request
Invalid request format or missing required fields

```json
{
  "detail": "Invalid email format"
}
```

### 401 Unauthorized
Authentication failed or token invalid

```json
{
  "detail": "Invalid username or password"
}
```

### 403 Forbidden
Insufficient permissions

```json
{
  "detail": "Access forbidden"
}
```

### 404 Not Found
Resource not found

```json
{
  "detail": "User not found"
}
```

### 409 Conflict
Resource already exists

```json
{
  "detail": "Username already exists"
}
```

### 422 Unprocessable Entity
Validation error

```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "password"],
      "msg": "Password must be at least 8 characters"
    }
  ]
}
```

### 500 Internal Server Error
Server-side error

```json
{
  "detail": "Internal server error"
}
```

---

## Testing Guide

### Using Swagger UI (Recommended)
1. Visit `http://localhost:8000/docs`
2. Click on **POST /register** → Try it out
3. Enter credentials and click Execute
4. Copy the `totp_secret` from response
5. Generate a TOTP code using an authenticator app or:
   ```bash
   python -c "import pyotp; print(pyotp.TOTP('YOUR_SECRET').now())"
   ```
6. Click on **POST /login** → Try it out
7. Enter username, password, and TOTP code
8. Click the 🔒 **Authorize** button at top-right
9. Paste the `access_token` and click **Authorize**
10. Now test protected endpoints like **GET /users/me**

### Using cURL

**Register User:**
```bash
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "SecureP@ss123!"
  }'
```

**Generate TOTP Code:**
```bash
python -c "import pyotp; print(pyotp.TOTP('RJCD6YAN2KIUFW7DV56FPPWDYDAZ3CKO').now())"
```

**Login:**
```bash
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "SecureP@ss123!",
    "totp": "123456"
  }'
```

**Get User Profile:**
```bash
curl -X GET http://localhost:8000/users/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Refresh Token:**
```bash
curl -X POST http://localhost:8000/token/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "YOUR_REFRESH_TOKEN"
  }'
```

**Logout:**
```bash
curl -X POST http://localhost:8000/logout \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "YOUR_REFRESH_TOKEN"
  }'
```

### Using PowerShell

**Register:**
```powershell
$body = @{
    username = "testuser"
    email = "test@example.com"
    password = "SecureP@ss123!"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/register" `
  -Method POST -Body $body -ContentType "application/json" | ConvertFrom-Json
```

**Login and Get Token:**
```powershell
$body = @{
    username = "testuser"
    password = "SecureP@ss123!"
    totp = "123456"
} | ConvertTo-Json

$response = Invoke-WebRequest -Uri "http://localhost:8000/login" `
  -Method POST -Body $body -ContentType "application/json" | ConvertFrom-Json

$token = $response.access_token
```

**Get Profile:**
```powershell
$headers = @{
    Authorization = "Bearer $token"
}

Invoke-WebRequest -Uri "http://localhost:8000/users/me" `
  -Method GET -Headers $headers | ConvertFrom-Json
```

### Using Python Requests

```python
import requests
import pyotp

BASE_URL = "http://localhost:8000"

# Register
reg = requests.post(f"{BASE_URL}/register", json={
    "username": "testuser",
    "email": "test@example.com",
    "password": "SecureP@ss123!"
}).json()

totp_secret = reg["totp_secret"]

# Login
totp = pyotp.TOTP(totp_secret)
login = requests.post(f"{BASE_URL}/login", json={
    "username": "testuser",
    "password": "SecureP@ss123!",
    "totp": totp.now()
}).json()

access_token = login["access_token"]

# Get Profile
headers = {"Authorization": f"Bearer {access_token}"}
profile = requests.get(f"{BASE_URL}/users/me", headers=headers).json()
print(profile)
```

### Automated Testing

Run the full test suite:
```bash
python tests/test_all_endpoints.py
```

This runs 12 tests covering:
- Health check
- Registration
- Login
- Profile retrieval
- Token refresh
- Logout
- Invalid credentials
- Unauthorized access
- Invalid token
- Weak password validation
- Email validation
- Token invalidation

---

## Notes

- All timestamps are in ISO 8601 format (UTC)
- Base64 encoding used for binary data
- Token expires in 900 seconds (15 minutes) for access tokens
- Refresh tokens expire in 7 days
- TOTP codes expire in 30 seconds from generation
- Clock drift tolerance: ±1 time step (±30 seconds)
- All cryptographic operations use industry-standard algorithms
- Database: SQLite (can be upgraded to PostgreSQL for production)
- ORM: SQLModel (Pydantic + SQLAlchemy)
