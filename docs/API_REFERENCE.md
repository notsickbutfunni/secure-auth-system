# API Endpoints Reference Guide

Base URL: `http://localhost:8000`

---

## Authentication Endpoints

### 1. User Registration
**POST** `/register`

**Request Body:**
```json
{
  "username": "myuser",
  "email": "user@example.com",
  "password": "SecureP@ss123!",
  "password_confirm": "SecureP@ss123!"
}
```

**Response (200):**
```json
{
  "msg": "User registered successfully",
  "username": "myuser",
  "email": "user@example.com",
  "totp_secret": "ABCD1234EFGH5678"
}
```

**Password Requirements:**
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit
- At least one special character

---

### 2. User Login
**POST** `/login`

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
  "access_token": "eyJhbGciOiJSUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 900
}
```

**Note:** TOTP code must be valid 6-digit code from authenticator app

---

### 3. Get All Users
**GET** `/users/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
[
  {
    "id": 1,
    "username": "user1",
    "email": "user1@example.com",
    "created_at": "2025-12-05T10:00:00"
  },
  {
    "id": 2,
    "username": "user2",
    "email": "user2@example.com",
    "created_at": "2025-12-05T10:05:00"
  }
]
```

---

## Encryption Test Endpoints

### 4. AES-256-GCM Encryption
**POST** `/test/encrypt`

**Request Body:**
```json
{
  "message": "Hello, secure world!"
}
```

**Response (200):**
```json
{
  "encrypted": "g3Y71ZfqTjK0KtS9Iq2kBScRLr3pBr2w4doDZxQTPOtGM/V3xl/sYwOR..."
}
```

**Algorithm:** AES-256-GCM with random 12-byte nonce

---

### 5. AES-256-GCM Decryption
**POST** `/test/decrypt`

**Request Body:**
```json
{
  "encrypted": "g3Y71ZfqTjK0KtS9Iq2kBScRLr3pBr2w4doDZxQTPOtGM/V3xl/sYwOR..."
}
```

**Response (200):**
```json
{
  "decrypted": "Hello, secure world!"
}
```

---

## RSA Key Wrapping Endpoints

### 6. RSA-OAEP Key Encryption
**POST** `/test/rsa/encrypt-key`

**Request Body:**
```json
{}
```

**Response (200):**
```json
{
  "msg": "RSA-OAEP encryption successful",
  "encrypted_aes_key": "fC/Vj+eE86b29T6ENzPJMIRd1CrKtOuEDwMXoGQLhvfl4B99ALfRWpAvOMa7...",
  "algorithm": "RSA-OAEP with SHA256"
}
```

**Algorithm:** RSA-OAEP with 2048-bit key and SHA256

---

### 7. RSA-OAEP Key Decryption
**POST** `/test/rsa/decrypt-key`

**Request Body:**
```json
{
  "encrypted_key": "fC/Vj+eE86b29T6ENzPJMIRd1CrKtOuEDwMXoGQLhvfl4B99ALfRWpAvOMa7..."
}
```

**Response (200):**
```json
{
  "msg": "RSA-OAEP decryption successful",
  "key_valid": true,
  "algorithm": "RSA-OAEP with SHA256"
}
```

---

## Digital Signature Endpoints

### 8. Sign Message (RSA-PSS)
**POST** `/test/sign`

**Request Body:**
```json
{
  "message": "This is a message to be signed"
}
```

**Response (200):**
```json
{
  "msg": "Message signed successfully",
  "message": "This is a message to be signed",
  "signature": "XmjO88xUkoTHMTUCPsu3ijsqdL/syaWdmUYXHKgj/KAOAdhRjhkqu87tl6Qv...",
  "algorithm": "RSA-PSS with SHA256"
}
```

**Algorithm:** RSA-PSS with 2048-bit key and SHA256

---

### 9. Verify Signature (RSA-PSS)
**POST** `/test/verify`

**Request Body:**
```json
{
  "message": "This is a message to be signed",
  "signature": "XmjO88xUkoTHMTUCPsu3ijsqdL/syaWdmUYXHKgj/KAOAdhRjhkqu87tl6Qv..."
}
```

**Response (200):**
```json
{
  "msg": "Signature verification complete",
  "message": "This is a message to be signed",
  "signature_valid": true,
  "algorithm": "RSA-PSS with SHA256"
}
```

---

## Diffie-Hellman Key Exchange Endpoints

### 10. Generate DH Key Pair
**POST** `/test/dh/generate-keys`

**Request Body:**
```json
{}
```

**Response (200):**
```json
{
  "msg": "DH key pair generated successfully",
  "private_key": "167712740067917915625386138753258297170972990235877336432091...",
  "public_key": "905317863965081905898892614521393387219808668640467249148788...",
  "algorithm": "Diffie-Hellman (RFC 3526 2048-bit)",
  "dh_parameters": {
    "p_bits": 1024,
    "g": 2
  }
}
```

---

### 11. Compute DH Shared Secret
**POST** `/test/dh/compute-shared-secret`

**Request Body:**
```json
{
  "my_private_key": "167712740067917915625386138753258297170972990235877336432091...",
  "peer_public_key": "905317863965081905898892614521393387219808668640467249148788..."
}
```

**Response (200):**
```json
{
  "msg": "Shared secret computed successfully",
  "shared_secret": "359856673110628124485441376545080733913346246719291864800103...",
  "algorithm": "Diffie-Hellman"
}
```

---

### 12. Derive AES Key from DH Shared Secret
**POST** `/test/dh/derive-aes-key`

**Request Body:**
```json
{
  "shared_secret": "359856673110628124485441376545080733913346246719291864800103...",
  "key_length": 32
}
```

**Response (200):**
```json
{
  "msg": "AES key derived from DH shared secret",
  "aes_key": "ObVR5CdnqcfVgNYZIjVG/uYfeU26bch/Z7RqReckca4=",
  "key_length_bytes": 32,
  "algorithm": "HKDF-SHA256",
  "info_context": "dh key agreement"
}
```

---

### 13. Complete DH Key Exchange (Alice & Bob)
**POST** `/test/dh/full-exchange`

**Request Body:**
```json
{}
```

**Response (200):**
```json
{
  "msg": "DH key exchange complete",
  "alice": {
    "public_key": "64827911315573497363746851832317858473714463163773...",
    "shared_secret": "143321330388848030087236682329130121258210950303914207782482...",
    "derived_aes_key": "PvRyfcltfQr+uuAojRgwpjtmNyymiaQg7ad1qMvULbc="
  },
  "bob": {
    "public_key": "75541949505112840443158047596683807166423358385918...",
    "shared_secret": "143321330388848030087236682329130121258210950303914207782482...",
    "derived_aes_key": "PvRyfcltfQr+uuAojRgwpjtmNyymiaQg7ad1qMvULbc="
  },
  "verification": {
    "shared_secrets_match": true,
    "aes_keys_match": true,
    "exchange_status": "SUCCESS"
  },
  "algorithm": "Diffie-Hellman (RFC 3526 2048-bit) + HKDF-SHA256"
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid request format or missing parameters"
}
```

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 422 Unprocessable Entity
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "password"],
      "msg": "Password does not meet complexity requirements"
    }
  ]
}
```

---

## Testing Guide

### Using cURL

**Register User:**
```bash
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "SecureP@ss123!",
    "password_confirm": "SecureP@ss123!"
  }'
```

**Encrypt Message:**
```bash
curl -X POST http://localhost:8000/test/encrypt \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, World!"}'
```

**Sign Message:**
```bash
curl -X POST http://localhost:8000/test/sign \
  -H "Content-Type: application/json" \
  -d '{"message": "Important document"}'
```

---

## Notes

- All timestamps are in ISO 8601 format (UTC)
- Base64 encoding used for binary data (encrypted values, signatures)
- Token expires in 900 seconds (15 minutes)
- TOTP tokens expire in 30 seconds from generation
- All cryptographic operations use industry-standard algorithms
- DH parameters are from RFC 3526 (2048-bit MODP Group)
