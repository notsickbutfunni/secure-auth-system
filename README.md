# Secure Authentication System

## Description
A secure authentication system built with FastAPI and modern web technologies. Features JWT-based authentication, multi-factor authentication (TOTP), AES-GCM encryption, RSA digital signatures, and a simple frontend.

## Features
- ✅ User registration with strong password validation
- ✅ JWT-based authentication (RS256 asymmetric signing)
- ✅ Access & Refresh token system
- ✅ TOTP-based 2FA (Time-based One-Time Password)
- ✅ Argon2 password hashing (memory-hard algorithm)
- ✅ AES-GCM encrypted token storage
- ✅ RSA-PSS digital signatures
- ✅ Diffie-Hellman key exchange (RFC 3526 2048-bit)
- ✅ SQLite database with SQLModel ORM
- ✅ CORS-enabled API
- ✅ Interactive Swagger UI documentation
- ✅ Responsive web frontend 
- ✅ Built-in documentation viewer on dashboard

## Tech Stack
**Backend:**
- FastAPI with Uvicorn
- SQLModel (SQLAlchemy ORM)
- PyJWT for JWT operations
- Argon2 for password hashing
- PyOTP for TOTP generation
- Cryptography library for encryption/signatures

**Frontend:**
- Vanilla HTML/CSS/JavaScript
- Comfortaa font 
- localStorage for token persistence
- Fetch API for backend communication

## Installation

### Prerequisites
- Python 3.8+
- pip

### Setup

1. **Clone the repository**
    ```bash
    git clone https://github.com/notsickbutfunni/secure-auth-system.git
    cd secure-auth-system
    ```

2. **Create virtual environment**
    ```bash
    python -m venv .venv
    ```

3. **Activate virtual environment**

    Windows:
    ```bash
    .venv\Scripts\activate
    ```

    Mac/Linux:
    ```bash
    source .venv/bin/activate
    ```

4. **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

5. **Generate encryption keys** (if not already present)
    ```bash
    python generate_keys.py
    ```

## Usage

### Start Backend Server
```bash
python -m uvicorn main:app --reload
```
Backend runs on `http://localhost:8000`

### Start Frontend Server
```bash
cd frontend
python -m http.server 5500
```
Frontend runs on `http://localhost:5500`

### Access Points
- **Login/Register:** http://localhost:5500
- **Dashboard:** http://localhost:5500/dashboard.html (after login)
- **API Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## API Endpoints

### Authentication
- `POST /register` - Create new user account
- `POST /login` - Authenticate and receive tokens
- `POST /token/refresh` - Refresh access token
- `POST /logout` - Invalidate refresh tokens
- `GET /users/me` - Get current user profile

### Status
- `GET /` - Health check

## Cryptographic Components
- **AES-256-GCM** - Authenticated encryption with 256-bit keys for token storage
- **RSA-2048** - Asymmetric encryption for key wrapping and digital signatures
- **RSA-PSS** - Probabilistic signature scheme with SHA-256 for message signing
- **Argon2id** - Memory-hard password hashing (resistant to GPU/ASIC attacks)
- **HKDF-SHA256** - Key derivation for Diffie-Hellman shared secrets
- **SHA-256** - Cryptographic hashing throughout the system

## Security Features

### Password Security
- Minimum 8 characters with uppercase, lowercase, digit, special character
- Argon2id hashing (no plain text storage)
- Input sanitization and validation

### Token Security
- Short-lived access tokens (15 minutes)
- Long-lived refresh tokens (7 days) with database tracking
- Encrypted refresh token storage in database
- RS256 asymmetric signing prevents token forgery

### Encryption
- AES-GCM provides both confidentiality and authenticity
- Random nonce per encryption operation
- Additional Authenticated Data (AAD) for context binding

### Additional Protection
- CORS properly configured
- Input validation on all endpoints
- Generic error messages (no information leakage)
- Secure random number generation (secrets module)
- Protected against: brute force, replay attacks, SQL injection

## Project Structure
```
secure-auth-system/
├── main.py                 # FastAPI application
├── requirements.txt        # Python dependencies
├── generate_keys.py        # Key generation script
├── db.sqlite              # SQLite database
├── keys/                  # Encryption keys (RSA, AES)
├── docs/                  # Documentation
├── tests/                 # Test suite
├── frontend/
│   ├── index.html         # Login/Register page
│   ├── dashboard.html     # User dashboard
│   ├── app.js             # Login logic
│   ├── dashboard.js       # Dashboard logic
│   ├── miku-chibi.png     # Miku animation asset
└── README.md
```

## Key Learnings
This project demonstrates:
- Secure authentication best practices
- Advanced cryptography applications
- JWT token lifecycle management
- Frontend-backend integration
- Database design with ORM
- API documentation and testing
- UI/UX with custom theming

## Security Considerations
- ⚠️ Use HTTPS in production (currently HTTP for dev)
- ⚠️ Implement rate limiting on login attempts
- ⚠️ Add request logging and audit trails
- ⚠️ Enable CSRF protection for state-changing operations
- ⚠️ Implement session management on backend
- ⚠️ Regular security audits and key rotation
- ⚠️ Secure key storage (use environment variables/secrets manager)

## Special Features
### 🎤 Easter Egg
The dashboard includes a secret button. Click the **🎤 Secret** button and type *the best teacher in the worlds name\* to unlock a special message!

## Team Members
- Inkar Khairatkyzy (GitHub: @notsickbutfunni)

## License
MIT License - See LICENSE file for details

## Acknowledgments
- Built with curiosity and love for learning security fundamentals
- Miku chibi theme as a tribute to Hatsune Miku
- Special thanks to [@weeebdev](https://github.com/weeebdev), whose expertise and encouragement made this course possible!
