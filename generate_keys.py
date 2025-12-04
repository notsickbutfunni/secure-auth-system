from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import os

# Create keys directory
os.makedirs("keys/rsa_aes_wrap", exist_ok=True)

# Generate RSA private key for JWT signing
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)

# Writing JWT private key
with open("keys/private.pem", "wb") as f:
    f.write(private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ))

# Writing JWT public key
with open("keys/public.pem", "wb") as f:
    f.write(private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ))


# Generate separate RSA key pair for AES key wrapping
rsa_wrap_private = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)

# Writing RSA AES wrapping private key
with open("keys/rsa_aes_wrap/private.pem", "wb") as f:
    f.write(rsa_wrap_private.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ))

# Writing RSA AES wrapping public key
with open("keys/rsa_aes_wrap/public.pem", "wb") as f:
    f.write(rsa_wrap_private.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ))

print("✓ JWT RSA keys generated (keys/private.pem, keys/public.pem)")
print("✓ AES wrapping RSA keys generated (keys/rsa_aes_wrap/private.pem, keys/rsa_aes_wrap/public.pem)")

