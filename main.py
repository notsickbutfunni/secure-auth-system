from fastapi import FastAPI, HTTPException, Depends, Body, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta
from typing import Optional
from sqlmodel import Field, SQLModel, create_engine, Session, select
from pydantic import BaseModel, field_validator
from argon2 import PasswordHasher
import pyotp
import re
import jwt
from argon2.exceptions import VerifyMismatchError
import os
import base64
import secrets
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

# -------------------------
# FastAPI app
# -------------------------
app = FastAPI(
    title="Secure Authentication System",
    description="Production-ready authentication API with JWT, TOTP, and encryption",
    version="1.0.0"
)

# CORS for local frontend (dev only). Adjust or tighten for production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security scheme for Swagger UI
security = HTTPBearer(auto_error=False)


# -------------------------
# All setups
# -------------------------

#for database
DB_URL = "sqlite:///db.sqlite"
engine = create_engine(DB_URL, echo=True)

# for AES key
AES_KEY_PATH = "keys/aes_key.bin"
KEY_SIZE = 32  # 256-bit
NONCE_SIZE = 12 

# for RSA key
RSA_KEY_PATH = "keys/rsa_aes_wrap"   
KEYS_DIR = "keys"

# Agon2 hasher
ph = PasswordHasher()


# --------------------------------------------------
# Key Management, Secure Randomness, Error Handling
# --------------------------------------------------

# keys loading
with open("keys/private.pem", "rb") as f:
    private_pem = f.read()
    PRIVATE_KEY = serialization.load_pem_private_key(private_pem, password=None)

with open("keys/public.pem", "rb") as f:
    public_pem = f.read()
    PUBLIC_KEY = serialization.load_pem_public_key(public_pem)

# Generate and load AES key
def generate_aes_key():
    os.makedirs("keys", exist_ok=True)
    key = secrets.token_bytes(KEY_SIZE)
    with open(AES_KEY_PATH, "wb") as f:
        f.write(key)
    return key

def load_aes_key():
    if not os.path.exists(AES_KEY_PATH):
        return generate_aes_key()
    with open(AES_KEY_PATH, "rb") as f:
        return f.read()
    
AES_KEY = load_aes_key()

def load_rsa_keys():
    with open(f"{RSA_KEY_PATH}/private.pem", "rb") as f:
        private_key = serialization.load_pem_private_key(f.read(), password=None)
    with open(f"{RSA_KEY_PATH}/public.pem", "rb") as f:
        public_key = serialization.load_pem_public_key(f.read())
    return private_key, public_key

private_rsa, public_rsa = load_rsa_keys()

def rsa_encrypt_aes_key(aes_key_bytes: bytes) -> str:
    """Encrypt AES key with RSA public key using OAEP"""
    ct = public_rsa.encrypt(
        aes_key_bytes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return base64.b64encode(ct).decode()

def rsa_decrypt_aes_key(ct_b64: str) -> bytes:
    """Decrypt AES key with RSA private key"""
    ct = base64.b64decode(ct_b64)
    pt = private_rsa.decrypt(
        ct,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return pt


# Secure Random Generation
import secrets

def secure_random_bytes(n: int = 32):
    return secrets.token_bytes(n)

def secure_random_string(n: int = 32):
    return secrets.token_hex(n)


# rsa key rotation
def rotate_rsa_key():
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    key_folder = os.path.join(KEYS_DIR, "rsa")
    os.makedirs(key_folder, exist_ok=True)

    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    with open(f"{key_folder}/{timestamp}_private.pem", "wb") as f:
        f.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
        )

    with open(f"{key_folder}/{timestamp}_public.pem", "wb") as f:
        f.write(
            private_key.public_key().public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
        )

    return timestamp

# aes key rotation
def rotate_aes_key():
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    key_folder = os.path.join(KEYS_DIR, "aes")
    os.makedirs(key_folder, exist_ok=True)

    key = secrets.token_bytes(32)  # AES-256
    with open(f"{key_folder}/aes_{timestamp}.key", "wb") as f:
        f.write(key)

    return timestamp

# Secure Key Loading
def load_latest_key(folder: str):
    path = os.path.join(KEYS_DIR, folder)
    files = sorted(os.listdir(path))
    if not files:
        raise RuntimeError(f"No keys in {folder}")
    return os.path.join(path, files[-1])

# Input Sanitization

def sanitize_username(username: str):
    if not re.match(r'^[A-Za-z0-9._-]{3,30}$', username):
        raise ValueError("Invalid username format")
    return username.strip()

def sanitize_email(email: str):
    email = email.strip()
    if "@" not in email or len(email) < 5:
        raise ValueError("Invalid email")
    return email


# Simple error handler functions 
def raise_invalid_credentials():
    raise HTTPException(status_code=401, detail="Invalid username or password")

def raise_invalid_totp():
    raise HTTPException(status_code=400, detail="Invalid TOTP code")

def raise_user_not_found():
    raise HTTPException(status_code=404, detail="User not found")

def raise_user_exists():
    raise HTTPException(status_code=409, detail="User already exists")

def raise_invalid_password():
    raise HTTPException(status_code=400, detail="Password does not meet security requirements")

def raise_invalid_email():
    raise HTTPException(status_code=400, detail="Invalid email format")

def raise_encryption_error():
    raise HTTPException(status_code=500, detail="Encryption operation failed")

def raise_decryption_error():
    raise HTTPException(status_code=500, detail="Decryption operation failed")

def raise_validation_error(msg: str):
    raise HTTPException(status_code=422, detail=msg)


# Simple input validation functions
def validate_username_simple(username: str) -> bool:
    """Validate username: 3-32 chars, alphanumeric + underscore/dash"""
    if not username or len(username) < 3 or len(username) > 32:
        return False
    return bool(re.match(r'^[a-zA-Z0-9_-]{3,32}$', username))

def validate_email_simple(email: str) -> bool:
    """Validate email format"""
    if not email or len(email) > 254:
        return False
    pattern = r'^[a-zA-Z0-9.!#$%&\'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$'
    return bool(re.match(pattern, email.lower()))

def validate_totp_code(code: str) -> bool:
    """Validate TOTP code: must be 6 digits"""
    if not code or len(code) != 6 or not code.isdigit():
        return False
    return True

def sanitize_input(value: str) -> str:
    """Remove dangerous characters and SQL keywords"""
    dangerous = ['<', '>', '"', "'", ';', '&', '|', '`', '$']
    for char in dangerous:
        value = value.replace(char, '')
    return value.strip()


# Simple secure randomness functions (Day 10)
def random_token(nbytes: int = 32) -> str:
    """Generate cryptographically secure random token (hex)"""
    return secrets.token_hex(nbytes)

def random_token_urlsafe(nbytes: int = 32) -> str:
    """Generate cryptographically secure random token (URL-safe)"""
    return secrets.token_urlsafe(nbytes)

def random_bytes(length: int = 32) -> bytes:
    """Generate cryptographically secure random bytes"""
    return secrets.token_bytes(length)

def random_nonce(length: int = 12) -> bytes:
    """Generate random nonce for AES-GCM (default 12 bytes)"""
    return secrets.token_bytes(length)


# -------------------------
# User model
# -------------------------

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: Optional[str] = None
    password_hash: str
    totp_secret: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class RefreshToken(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    encrypted_token: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime



class UserCreate(BaseModel):
    username: str
    email: str
    password_hash: str


# -------------------------
# Pydantic schema for registration
# -------------------------

class Registering(BaseModel):
    username: str
    email: str
    password: str
    
    @field_validator('username')
    def username_valid(cls, v):
        if len(v) < 3:
            raise ValueError('Username too short (min 3 chars)')
        return v
    
    @field_validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must include an uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must include a lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must include a digit')
        if not re.search(r'[\W_]', v):
            raise ValueError('Password must include a special character')
        return v
        
        
        
# -------------------------
# JWT Generate 
# -------------------------
class LoginSchema(BaseModel):
    username: str
    password: str
    totp: Optional[str] = None


def create_access_token(username: str):
    payload = {
        "sub": username,
        "type": "access",
        "exp": datetime.utcnow() + timedelta(minutes=15)
    }
    return jwt.encode(payload, PRIVATE_KEY, algorithm="RS256")


def create_refresh_token(username: str):
    payload = {
        "sub": username,
        "type": "refresh",
        "exp": datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, PRIVATE_KEY, algorithm="RS256")


# ---------------------------
# Encryption / Decryption
# ---------------------------
def encrypt_aes_gcm(plaintext: bytes, aad: bytes = None) -> str:
    nonce = secrets.token_bytes(NONCE_SIZE)
    aesgcm = AESGCM(AES_KEY)
    ciphertext = aesgcm.encrypt(nonce, plaintext, aad)
    combined = nonce + ciphertext
    return base64.b64encode(combined).decode()


def decrypt_aes_gcm(token_b64: str, aad: bytes = None) -> bytes:
    combined = base64.b64decode(token_b64)
    nonce = combined[:NONCE_SIZE]
    ciphertext = combined[NONCE_SIZE:]
    aesgcm = AESGCM(AES_KEY)
    return aesgcm.decrypt(nonce, ciphertext, aad)


# -------------------------
# Digital Signatures (RSA-PSS)
# -------------------------

def sign_message(message: bytes) -> str:
    """Sign a message using RSA-PSS"""
    signature = PRIVATE_KEY.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return base64.b64encode(signature).decode()


def verify_signature(message: bytes, signature_b64: str) -> bool:
    """Verify RSA-PSS signature"""
    signature = base64.b64decode(signature_b64)
    try:
        PUBLIC_KEY.verify(
            signature,
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except Exception:
        return False
    

# -----------------------------------
# Diffie-Hellman (DH) key exchange (RFC 3526 - 2048-bit MODP Group)
# -----------------------------------

# Large prime (P) for DH - RFC 3526 2048-bit MODP Group
P = 0xFFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD129024E088A67CC74020BBEA63B139B22514A08798E3404DDEF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7EDEE386BFB5A899FA5AE9F24117C4B1FE649286651ECE65381FFFFFFFFFFFFFFFF

# Generator (G) for DH
G = 2

def dh_generate_private_key() -> int:
    """Generate a random private key (secret)"""
    return secrets.randbelow(P - 2) + 1  # 1 <= private < P-1

def dh_generate_public_key(private_key: int) -> int:
    """Compute public key g^a mod p"""
    return pow(G, private_key, P)

def dh_compute_shared_secret(private_key: int, other_public_key: int) -> int:
    """Compute shared secret: other_pub^priv mod p"""
    return pow(other_public_key, private_key, P)

def dh_derive_aes_key(shared_secret: int, length: int = 32) -> bytes:
    """Derive AES key from shared secret integer using HKDF-SHA256"""
    shared_bytes = shared_secret.to_bytes((shared_secret.bit_length() + 7) // 8, "big")
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=length,
        salt=None,
        info=b"dh key agreement",
    )
    return hkdf.derive(shared_bytes)



# -------------------------
# endpoints
# -------------------------

@app.get("/")
def root():
    return {"message": "Secure Authentication System API", "version": "1.0", "status": "running"}


# -------------------------
# Authentication Endpoints
# -------------------------

# Registration endpoint
@app.post("/register")
def register(user: Registering):
    with Session(engine) as session:
        # Validate email format
        if not validate_email_simple(user.email):
            raise_invalid_email()
        
        existing = session.exec(select(User).where(User.username == user.username.lower())).first()
        if existing:
            raise HTTPException(status_code=409, detail="Username already exists")

        # Hash password
        password_hash = ph.hash(user.password)

        # Generate TOTP secret
        totp_secret = pyotp.random_base32()

        db_user = User(
            username=user.username.lower(),
            email=user.email.lower().strip(),
            password_hash=password_hash,
            totp_secret=totp_secret
        )
        session.add(db_user)
        session.commit()
        session.refresh(db_user)

    return {
        "msg": "User registered successfully",
        "username": db_user.username,
        "email": db_user.email,
        "totp_secret": db_user.totp_secret  
    }


# Login endpoint
@app.post("/login")
def login(data: LoginSchema):
    with Session(engine) as session:
        user = session.exec(
            select(User).where(User.username == data.username.lower())
        ).first()

        if not user:
            raise HTTPException(status_code=401, detail="Invalid username or password")

        # Verify password
        try:
            ph.verify(user.password_hash, data.password)
        except VerifyMismatchError:
            raise HTTPException(status_code=401, detail="Invalid username or password")

        # # Verify TOTP
        # if not user.totp_secret:
        #     raise HTTPException(status_code=400, detail="TOTP not configured for this user")
        
        # totp = pyotp.TOTP(user.totp_secret)
        # if not totp.verify(data.totp, valid_window=1):
        #     raise HTTPException(status_code=401, detail="Invalid TOTP code")

        # Create tokens
        access = create_access_token(user.username)
        refresh = create_refresh_token(user.username)
        
        # Encrypt refresh token for storage
        encrypted_refresh = encrypt_aes_gcm(refresh.encode(), aad=user.username.encode())
        
        # Store encrypted refresh token
        expires_at = datetime.utcnow() + timedelta(days=7)
        db_refresh = RefreshToken(user_id=user.id, encrypted_token=encrypted_refresh, expires_at=expires_at)
        session.add(db_refresh)
        session.commit()

        return {
            "msg": "Login successful",
            "access_token": access,
            "refresh_token": refresh,
            "token_type": "bearer"
        }




# -------------------------
# Token Management Endpoints
# -------------------------

# Token refresh endpoint
@app.post("/token/refresh")
def refresh_token(data: dict = Body(...)):
    """Refresh access token using refresh token"""
    refresh_token_str = data.get("refresh_token", "")
    
    if not refresh_token_str:
        raise HTTPException(status_code=400, detail="Refresh token required")
    
    try:
        # Decode refresh token
        payload = jwt.decode(refresh_token_str, PUBLIC_KEY, algorithms=["RS256"])
        
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=400, detail="Invalid token type")
        
        username = payload.get("sub")
        
        # Verify token exists in database
        with Session(engine) as session:
            user = session.exec(select(User).where(User.username == username)).first()
            if not user:
                raise HTTPException(status_code=401, detail="User not found")
            
            # Check if refresh token exists and is not expired
            stored_token = session.exec(
                select(RefreshToken)
                .where(RefreshToken.user_id == user.id)
                .where(RefreshToken.expires_at > datetime.utcnow())
            ).first()
            
            if not stored_token:
                raise HTTPException(status_code=401, detail="Refresh token expired or invalid")
            
            # Create new access token
            new_access = create_access_token(username)
            
            return {
                "msg": "Token refreshed successfully",
                "access_token": new_access,
                "token_type": "bearer"
            }
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")


# Logout endpoint
@app.post("/logout")
def logout(data: dict = Body(...)):
    """Logout user by invalidating refresh token"""
    refresh_token_str = data.get("refresh_token", "")
    
    if not refresh_token_str:
        raise HTTPException(status_code=400, detail="Refresh token required")
    
    try:
        # Decode refresh token
        payload = jwt.decode(refresh_token_str, PUBLIC_KEY, algorithms=["RS256"])
        username = payload.get("sub")
        
        with Session(engine) as session:
            user = session.exec(select(User).where(User.username == username)).first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            # Delete all refresh tokens for this user
            tokens = session.exec(
                select(RefreshToken).where(RefreshToken.user_id == user.id)
            ).all()
            
            for token in tokens:
                session.delete(token)
            
            session.commit()
        
        return {"msg": "Logged out successfully"}
    
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=400, detail="Invalid refresh token")


# -------------------------
# JWT Authentication Middleware
# -------------------------

def verify_access_token(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> str:
    """Dependency to verify JWT access token from Authorization header"""
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    token = credentials.credentials
    
    try:
        # Decode and verify JWT
        payload = jwt.decode(token, PUBLIC_KEY, algorithms=["RS256"])
        
        # Verify token type
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=401,
                detail="Invalid token type. Expected access token",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Extract username from token
        username = payload.get("sub")
        if not username:
            raise HTTPException(
                status_code=401,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        return username
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Access token has expired",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid access token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"}
        )


# -------------------------
# User Profile Endpoint
# -------------------------

@app.get("/users/me")
def get_current_user(username: str = Depends(verify_access_token)):
    """Get current authenticated user profile"""
    with Session(engine) as session:
        user = session.exec(
            select(User).where(User.username == username)
        ).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "created_at": user.created_at.isoformat(),
            "totp_enabled": bool(user.totp_secret)
        }

# -------------------------
# DB Initializing 
# -------------------------

def init_db():
    SQLModel.metadata.create_all(engine)

init_db()