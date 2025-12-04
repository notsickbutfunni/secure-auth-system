from fastapi import FastAPI, HTTPException, Depends
from datetime import datetime, timedelta
from typing import Optional
from sqlmodel import Field, SQLModel, create_engine, Session, select
from pydantic import BaseModel, EmailStr, field_validator
from argon2 import PasswordHasher
import pyotp
import re
import jwt
from argon2.exceptions import VerifyMismatchError

# -------------------------
# FastAPI app
# -------------------------
app = FastAPI(title="Secure Authentication System")


# -------------------------
# All setups
# -------------------------

#for database
DB_URL = "sqlite:///db.sqlite"
engine = create_engine(DB_URL, echo=True)


# Agon2 hasher
ph = PasswordHasher()


# keys loading
with open("keys/private.pem", "rb") as f:
    PRIVATE_KEY = f.read()

with open("keys/public.pem", "rb") as f:
    PUBLIC_KEY = f.read()



# -------------------------
# User model
# -------------------------

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: Optional[str] = None
    password_hash: str
    totp_secret: Optional[str] = None



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
    totp: str


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



# -------------------------
# DB Initializing 
# -------------------------

def init_db():
    SQLModel.metadata.create_all(engine)

init_db()

# -------------------------
# endpoints
# -------------------------

# main endpoint
@app.get("/")
def root():
    return {"message": "FastAPI server running!"}


# showing user info
@app.post("/users/")
def create_user(user: UserCreate):
    db_user = User(username=user.username, email=user.email, password_hash=user.password_hash)
    with Session(engine) as session:
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
    return {"id": db_user.id, "username": db_user.username, "email": db_user.email}

@app.get("/users/")
def list_users():
    with Session(engine) as session:
        users = session.exec(select(User)).all()
    return users



# registrayion endpoint
@app.post("/register")
def register(user: Registering):
    with Session(engine) as session:
        existing = session.exec(select(User).where(User.username == user.username.lower())).first()
        if existing:
            raise HTTPException(status_code=400, detail="Username already exists")

        # Hash password
        password_hash = ph.hash(user.password)

        # Generate TOTP secret
        totp_secret = pyotp.random_base32()

        db_user = User(
            username=user.username.lower(),
            email=user.email,
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
    
    
    
# login endpoint
@app.post("/login")
def login(data: LoginSchema):
    with Session(engine) as session:
        user = session.exec(
            select(User).where(User.username == data.username.lower())
        ).first()

        if not user:
            raise HTTPException(status_code=400, detail="Invalid username or password")

        # Verify password
        try:
            ph.verify(user.password_hash, data.password)
        except VerifyMismatchError:
            raise HTTPException(status_code=400, detail="Invalid username or password")

        # Verify TOTP
        if not user.totp_secret:
            raise HTTPException(status_code=400, detail="TOTP not configured for this user")
        
        totp = pyotp.TOTP(user.totp_secret)
        if not totp.verify(data.totp):
            raise HTTPException(status_code=400, detail="Invalid TOTP code")

        # Create tokens
        access = create_access_token(user.username)
        refresh = create_refresh_token(user.username)

        return {
            "msg": "Login successful",
            "access_token": access,
            "refresh_token": refresh,
            "token_type": "bearer"
        }



# @app.get("/auth/test")
# def test_auth():
#     return {"status": "auth endpoint works"}


# -------------------------
# Unit test for hashing (can be run separately)
# # -------------------------
# def test_hash():
#     password = "StrongPass1!"
#     hash1 = ph.hash(password)
#     hash2 = ph.hash(password)
#     assert hash1 != hash2, "Hashes must differ (unique salts)"
#     ph.verify(hash1, password)
#     ph.verify(hash2, password)
#     print("Argon2 hashing test passed.")

# if __name__ == "__main__":
#     test_hash()
