from __future__ import annotations
import os
import time
import uuid
from hashlib import sha256
from typing import Optional, Tuple, Dict, Any

# hashing
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

# for jwt 
import jwt
import time
import os
from typing import Tuple


# Configure Argon2 parameters from env (sensible defaults)
_ARGON2_TIME_COST = int(os.getenv("ARGON2_TIME_COST", "2"))
_ARGON2_MEMORY_COST = int(os.getenv("ARGON2_MEMORY_COST", "102400"))
_ARGON2_PARALLELISM = int(os.getenv("ARGON2_PARALLELISM", "8"))

ph = PasswordHasher(time_cost=_ARGON2_TIME_COST, 
                    memory_cost=_ARGON2_MEMORY_COST, 
                    parallelism=_ARGON2_PARALLELISM)


def hash_password(plain: str) -> str:
    """Hash a password using Argon2id"""
    return ph.hash(plain)


def verify_password(stored_hash: str, plain: str) -> bool:
    """Verify a password against the stored hash"""
    try:
        return ph.verify(stored_hash, plain)
    except VerifyMismatchError:
        return False
    except Exception:
        # Any other error treat as verification failure
        return False


def hash_jti(jti: str) -> str:
    """Hash a JTI value for safe storage (e.g., in DB)."""
    return sha256(jti.encode("utf-8")).hexdigest()

# jwt tokens
def _now_seconds() -> int:
    return int(time.time())


def create_access_token(sub: str, expires_minutes: int = 15) -> Tuple[str, str]:
    """Create a simple HS256 access token and return (token, jti).

    Uses `HS_SECRET` env var or a dev default. This is minimal for testing.
    """
    hs = os.environ.get("HS_SECRET", "dev-secret-change-me")
    now = _now_seconds()
    jti = str(uuid.uuid4())
    exp = now + expires_minutes * 60
    payload = {"sub": sub, "iat": now, "exp": exp, "jti": jti}
    token = jwt.encode(payload, hs, algorithm="HS256")
    return token, jti


def create_refresh_token(sub: str, expires_days: int = 30) -> Tuple[str, str]:
    """Create a HS256 refresh token (for testing) and return (token, jti)."""
    hs = os.environ.get("HS_SECRET", "dev-secret-change-me")
    now = _now_seconds()
    jti = str(uuid.uuid4())
    exp = now + expires_days * 24 * 3600
    payload = {"sub": sub, "iat": now, "exp": exp, "jti": jti}
    token = jwt.encode(payload, hs, algorithm="HS256")
    return token, jti


def verify_token_hs(token: str) -> dict:
    hs = os.environ.get("HS_SECRET", "dev-secret-change-me")
    return jwt.decode(token, hs, algorithms=["HS256"])
