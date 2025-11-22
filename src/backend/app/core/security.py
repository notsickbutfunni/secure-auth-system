from __future__ import annotations


import os
import time
import uuid
from hashlib import sha256
from typing import Optional, Tuple, Dict, Any

# hashing
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

# for jwt it will be added soon


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
