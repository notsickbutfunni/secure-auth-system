# Secure Authentication System - Architecture

## Overview

The Secure Authentication System is a production-ready FastAPI application that implements a comprehensive authentication and authorization framework with advanced cryptographic security features.

**Key Features:**
- JWT-based authentication with RS256 (RSA + SHA-256)
- Two-Factor Authentication (2FA) using TOTP
- Password hashing with Argon2id
- Refresh token encryption with AES-256-GCM
- HTTPBearer security scheme for API documentation

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Client Application                        │
│              (Web Browser, Mobile App, CLI)                  │
└──────────────────────────┬──────────────────────────────────┘
                           │
                ┌──────────▼──────────┐
                │  HTTP/HTTPS (TLS)   │
                └──────────┬──────────┘
                           │
        ┌──────────────────▼──────────────────┐
        │        FastAPI Web Server           │
        │      (Uvicorn ASGI Server)          │
        └──────────────────┬──────────────────┘
                           │
        ┌──────────────────▼──────────────────┐
        │      Routing & Middleware            │
        │   ├─ HTTPBearer Security Scheme      │
        │   ├─ JWT Verification Middleware    │
        │   └─ TOTP Validation                │
        └──────────────────┬──────────────────┘
                           │
        ┌──────────────────▼──────────────────┐
        │      6 Core API Endpoints           │
        │   ├─ GET /                          │
        │   ├─ POST /register                 │
        │   ├─ POST /login                    │
        │   ├─ POST /token/refresh            │
        │   ├─ POST /logout                   │
        │   └─ GET /users/me                  │
        └──────────────────┬──────────────────┘
                           │
        ┌──────────────────▼──────────────────┐
        │    Cryptography & Security Layer    │
        │   ├─ RSA-2048 Key Management        │
        │   ├─ AES-256-GCM Encryption         │
        │   ├─ Argon2id Password Hashing      │
        │   ├─ TOTP Generation & Validation   │
        │   └─ JWT Encoding/Decoding          │
        └──────────────────┬──────────────────┘
                           │
        ┌──────────────────▼──────────────────┐
        │      Database Layer (SQLModel)      │
        │         SQLite (Default)            │
        │     ├─ User Table                   │
        │     └─ RefreshToken Table           │
        └──────────────────┬──────────────────┘
                           │
        ┌──────────────────▼──────────────────┐
        │    Persistent Storage               │
        │   ├─ db.sqlite (Database)           │
        │   ├─ keys/private.pem (RSA)         │
        │   ├─ keys/public.pem (RSA)          │
        │   ├─ keys/aes_key.bin (AES)         │
        │   └─ keys/rsa_aes_wrap/ (Backup)    │
        └─────────────────────────────────────┘
```

---

## Component Details

### 1. FastAPI Application (`main.py`)

**Purpose:** Main entry point and request routing

**Key Components:**
- FastAPI app initialization with metadata
- HTTPBearer security scheme configuration
- 6 production endpoints
- Request/response handling

**Code Structure:**
```python
from fastapi import FastAPI
from fastapi.security import HTTPBearer

app = FastAPI(
    title="Secure Authentication System",
    version="1.0.0"
)

security = HTTPBearer(auto_error=False)
```

**Lines:** ~750 total

---

### 2. Database Models (SQLModel)

**User Table:**
```python
class User(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True)
    username: str = Field(index=True, unique=True)
    email: Optional[str] = None
    password_hash: str
    totp_secret: Optional[str] = None
    created_at: datetime
```

**RefreshToken Table:**
```python
class RefreshToken(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    encrypted_token: str  # AES-256-GCM encrypted
    created_at: datetime
    expires_at: datetime
```

**Database:**
- Default: SQLite (`db.sqlite`)
- Can upgrade to PostgreSQL for production
- ORM: SQLModel (Pydantic + SQLAlchemy hybrid)

---

### 3. Authentication Endpoints

#### GET `/` - Health Check
- **Purpose:** Verify API is running
- **Auth Required:** No
- **Response:** Status, version, message

#### POST `/register` - User Registration
- **Purpose:** Create new user with TOTP 2FA setup
- **Auth Required:** No
- **Input Validation:** 
  - Username: 3-32 alphanumeric chars, underscores, dashes
  - Email: RFC-compliant format
  - Password: 8+ chars, upper, lower, digit, special char
- **Output:** User data + TOTP secret
- **Encryption:** Passwords hashed with Argon2id

#### POST `/login` - User Authentication
- **Purpose:** Verify credentials and 2FA, issue tokens
- **Auth Required:** No
- **Process:**
  1. Verify username exists
  2. Verify password using Argon2id
  3. Verify TOTP code (±1 time window tolerance)
  4. Generate JWT access token (15 min)
  5. Generate JWT refresh token (7 days)
  6. Encrypt and store refresh token
  7. Return both tokens
- **Response:** Access token + Refresh token

#### POST `/token/refresh` - Token Refresh
- **Purpose:** Get new access token without re-authenticating
- **Auth Required:** No (uses refresh token in body)
- **Process:**
  1. Decode refresh token
  2. Verify token type is "refresh"
  3. Check token stored in database
  4. Verify expiration
  5. Generate new access token
- **Response:** New access token

#### POST `/logout` - User Logout
- **Purpose:** Invalidate all refresh tokens
- **Auth Required:** No (uses refresh token in body)
- **Side Effects:**
  - Deletes all refresh tokens from database
  - Existing access tokens remain valid until expiration
  - User must re-login for new tokens

#### GET `/users/me` - Current User Profile
- **Purpose:** Retrieve authenticated user profile
- **Auth Required:** Yes (HTTPBearer + JWT)
- **Dependency:** `verify_access_token()`
- **Response:** User ID, username, email, TOTP status, creation date

---

### 4. Security & Cryptography

#### JWT Authentication (RS256)

**Algorithm:** RSA Signature with SHA-256
- **Key Size:** 2048-bit RSA
- **Purpose:** Token integrity and authenticity verification

**Access Token:**
```json
{
  "sub": "username",
  "type": "access",
  "exp": 1733012345
}
```
- **Lifetime:** 15 minutes (900 seconds)
- **Use:** Protected endpoint authentication

**Refresh Token:**
```json
{
  "sub": "username",
  "type": "refresh",
  "exp": 1733617145
}
```
- **Lifetime:** 7 days (604,800 seconds)
- **Use:** Obtaining new access tokens
- **Storage:** Encrypted in database with AES-256-GCM

#### Password Hashing (Argon2id)

**Algorithm:** Argon2id (memory-hard, GPU-resistant)
- **Purpose:** Secure password storage
- **Features:**
  - Resistant to GPU/ASIC attacks
  - Configurable time/memory costs
  - Built-in salt generation
  - Industry standard (OWASP recommended)

#### Two-Factor Authentication (TOTP)

**Algorithm:** Time-based One-Time Password (RFC 6238)
- **Purpose:** Second authentication factor
- **Code Generation:**
  - 6-digit numeric codes
  - 30-second time steps
  - HMAC-SHA1 based
  - Compatible with standard authenticator apps

**Time Window:**
- Current code: valid
- Previous code: valid (±1 step = ±30 seconds)
- Total window: 90 seconds tolerance
- **Reason:** Accounts for client/server clock skew

#### Data Encryption (AES-256-GCM)

**Algorithm:** AES-256 in Galois/Counter Mode
- **Purpose:** Encrypt sensitive data (refresh tokens)
- **Parameters:**
  - Key: 256-bit (32 bytes)
  - Nonce: 12 bytes (random, per-encryption)
  - Authenticated Encryption: Yes (GCM provides both encryption and authentication)

**Process:**
1. Generate random 12-byte nonce
2. Encrypt data with AES-256-GCM
3. Combine nonce + ciphertext
4. Base64 encode for storage/transmission

---

### 5. Key Management

**RSA Keys (2048-bit):**
- **Private Key:** `keys/private.pem` (JWT signing)
- **Public Key:** `keys/public.pem` (JWT verification)
- **Backup:** `keys/rsa_aes_wrap/` (timestamped versions)
- **Rotation:** Function available: `rotate_rsa_key()`

**AES Keys (256-bit):**
- **Master Key:** `keys/aes_key.bin` (refresh token encryption)
- **Generation:** Automatic on first run if missing
- **Rotation:** Function available: `rotate_aes_key()`

**Key Files Must Be:**
- Restricted permissions (600 or equivalent)
- Backed up securely
- Rotated periodically in production
- Never committed to version control

---

### 6. Input Validation & Sanitization

**Username Validation:**
- Pattern: `^[a-zA-Z0-9_-]{3,32}$`
- No special characters except underscore/dash
- Case-insensitive (stored as lowercase)

**Email Validation:**
- RFC 5322 compliant regex
- Max length: 254 characters
- Case-insensitive (stored as lowercase)

**Password Validation:**
- Minimum 8 characters
- At least one uppercase letter (A-Z)
- At least one lowercase letter (a-z)
- At least one digit (0-9)
- At least one special character

**TOTP Code Validation:**
- Exactly 6 digits
- RFC 6238 compliant
- ±1 time step window

**Input Sanitization:**
- `sanitize_input()` removes dangerous characters
- Pydantic models validate types/formats
- SQL injection protection via SQLAlchemy ORM

---

### 7. Error Handling

**HTTP Status Codes:**
- `200/201` - Success
- `400` - Bad request (invalid input)
- `401` - Unauthorized (auth failed)
- `403` - Forbidden (insufficient permissions)
- `404` - Not found (user doesn't exist)
- `409` - Conflict (duplicate username)
- `422` - Validation error (Pydantic)
- `500` - Internal server error

**Error Response Format:**
```json
{
  "detail": "Error description"
}
```

**Helper Functions:**
- `raise_invalid_credentials()`
- `raise_user_not_found()`
- `raise_user_exists()`
- `raise_invalid_password()`
- `raise_invalid_email()`
- `raise_invalid_totp()`

---

## Data Flow

### Registration Flow

```
1. Client POST /register
   {username, email, password}
            ↓
2. Validate inputs (username, email, password strength)
            ↓
3. Check username uniqueness
            ↓
4. Hash password with Argon2id
            ↓
5. Generate TOTP secret (base32)
            ↓
6. Create User record in database
            ↓
7. Return user data + TOTP secret to client
            ↓
8. Client stores TOTP secret in authenticator app
```

### Login Flow

```
1. Client POST /login
   {username, password, totp}
            ↓
2. Query user by username
            ↓
3. Verify password with Argon2id
            ↓
4. Verify TOTP code (within ±1 window)
            ↓
5. Generate JWT access token (15 min)
            ↓
6. Generate JWT refresh token (7 days)
            ↓
7. Encrypt refresh token with AES-256-GCM
            ↓
8. Store encrypted token in RefreshToken table
            ↓
9. Return access_token + refresh_token to client
            ↓
10. Client stores tokens (access token in memory, refresh in secure storage)
```

### Protected Request Flow

```
1. Client GET /users/me
   Authorization: Bearer <access_token>
            ↓
2. HTTPBearer extracts token from header
            ↓
3. verify_access_token() dependency:
   - Decode JWT with public key
   - Verify signature (RS256)
   - Check token type is "access"
   - Check not expired
   - Extract username
            ↓
4. Route handler receives verified username
            ↓
5. Query user from database
            ↓
6. Return user profile
```

### Token Refresh Flow

```
1. Client POST /token/refresh
   {refresh_token}
            ↓
2. Decode refresh token (JWT)
            ↓
3. Verify token type is "refresh"
            ↓
4. Extract username
            ↓
5. Query user by username
            ↓
6. Verify refresh token stored in database
            ↓
7. Check expiration date
            ↓
8. Generate NEW access token
            ↓
9. Return new access token to client
```

### Logout Flow

```
1. Client POST /logout
   {refresh_token}
            ↓
2. Decode refresh token (JWT)
            ↓
3. Extract username
            ↓
4. Query user by username
            ↓
5. Delete ALL refresh tokens from RefreshToken table
            ↓
6. Commit database changes
            ↓
7. Return success message
            ↓
8. Existing access tokens remain valid (15 min)
            ↓
9. User must login again after expiration
```

---

## Security Considerations

### Password Storage
✅ Argon2id hashing (memory-hard, GPU-resistant)
✅ Automatic salt generation
✅ Configurable time/memory costs
⚠️ Never log passwords
⚠️ Never store plaintext passwords

### Token Security
✅ RS256 signature verification
✅ Expiration validation
✅ Token type validation
✅ Refresh tokens encrypted in database
✅ Token storage in database with expiration tracking
⚠️ Access tokens must be sent over HTTPS
⚠️ Refresh tokens must be stored securely (HTTP-only cookies recommended)

### 2FA Security
✅ TOTP with ±1 window tolerance
✅ Standard RFC 6238 compliant
✅ 6-digit codes (1 million combinations)
✅ 30-second refresh rate
⚠️ TOTP secret must be saved securely
⚠️ Backup codes recommended for recovery

### Key Security
✅ RSA 2048-bit keys (adequate for 2025)
✅ AES-256 (sufficient for next 20+ years)
✅ Key rotation functions available
✅ Secure random generation for nonces
⚠️ Keys must never be committed to version control
⚠️ Keys must have restricted file permissions (600)
⚠️ Keys must be backed up to secure location

### Input Validation
✅ Username/email regex validation
✅ Password strength requirements
✅ TOTP code format validation
✅ Pydantic type validation
✅ SQL injection prevention via ORM
⚠️ Always validate on server side
⚠️ Never trust client input

### HTTPS/TLS
⚠️ Production MUST use HTTPS
⚠️ Use valid SSL/TLS certificates
⚠️ Enable HSTS headers
⚠️ Use secure cookies (HTTPOnly, Secure flags)

---

## Deployment Architecture

### Development
```
Local Machine
├─ FastAPI App (Uvicorn)
├─ SQLite Database
└─ Cryptographic Keys
```

### Production (Recommended)
```
┌─────────────────────────────────────┐
│      Load Balancer / Reverse Proxy   │
│         (Nginx / HAProxy)            │
│         HTTPS/TLS Termination        │
└────────────┬────────────────────────┘
             │
    ┌────────┴────────┐
    │                 │
┌───▼──┐          ┌──▼───┐
│ App  │          │ App  │  (Multiple Instances)
│  1   │          │  2   │  (Uvicorn/Gunicorn)
└───┬──┘          └──┬───┘
    │                │
    └────────┬───────┘
             │
    ┌────────▼────────┐
    │   PostgreSQL    │  (or MySQL/MariaDB)
    │    Database     │  (Replicated)
    └─────────────────┘
    
    ┌─────────────────┐
    │ Secure Storage  │
    │  (Vault/KMS)    │  (For cryptographic keys)
    └─────────────────┘
```

---

## Testing Architecture

**Test File:** `tests/test_all_endpoints.py`

**Test Coverage (12 tests):**
1. Health Check (GET /)
2. User Registration
3. User Login
4. Get User Profile
5. Token Refresh
6. User Logout
7. Invalid Credentials (Security)
8. Unauthorized Access (Security)
9. Invalid Token (Security)
10. Weak Password Validation
11. Email Validation
12. Token Invalidation After Logout

**Testing Tools:**
- `requests` - HTTP client library
- `pyotp` - TOTP code generation
- Color-coded output for pass/fail visualization

---

## Performance Considerations

### Database Indexing
- `User.username` - indexed and unique
- `RefreshToken.user_id` - indexed (foreign key)

### Caching Opportunities
- User profile (short TTL)
- JWT public key verification results
- TOTP secret cache (not recommended)

### Scaling Considerations
- Stateless: Each request can be handled by any server
- Database connection pooling required for multiple instances
- Consider Redis for session management in future
- Database replication for high availability

---

## Future Enhancements

1. **OAuth2/OIDC Integration**
   - Google, GitHub, Microsoft login
   - Third-party authentication

2. **Advanced 2FA Methods**
   - SMS/Email codes
   - Backup codes for recovery
   - WebAuthn/FIDO2 support

3. **Rate Limiting**
   - Login attempt throttling
   - API rate limits per user

4. **Audit Logging**
   - Login history
   - Token usage tracking
   - Security event logs

5. **Role-Based Access Control (RBAC)**
   - User roles and permissions
   - Resource-level authorization

6. **Account Recovery**
   - Password reset flow
   - Email verification
   - Account lockout mechanisms

7. **Device Management**
   - Track login devices
   - Require re-authentication for new devices
   - Remote device logout

---

## References

- [RFC 6238 - TOTP](https://tools.ietf.org/html/rfc6238)
- [RFC 7519 - JWT](https://tools.ietf.org/html/rfc7519)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [Argon2 Official](https://github.com/P-H-C/phc-winner-argon2)
- [AES-GCM Specification](https://csrc.nist.gov/publications/detail/sp/800-38d/final)
