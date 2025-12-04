from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

# Generate RSA private key
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)

# Writing private key
with open("keys/private.pem", "wb") as f:
    f.write(private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ))

# Writing public key
with open("keys/public.pem", "wb") as f:
    f.write(private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ))
    
# Writing 
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

# print("RSA keys generated!")
