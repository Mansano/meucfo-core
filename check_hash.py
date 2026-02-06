
from passlib.context import CryptContext
import sys

print("Testing password hashing...")
try:
    pwd_context = CryptContext(
        schemes=["bcrypt_sha256"],
        default="bcrypt_sha256",
        deprecated="auto",
    )
    hash = pwd_context.hash("testpassword")
    print(f"Hash created: {hash}")
    verify = pwd_context.verify("testpassword", hash)
    print(f"Verification: {verify}")
except Exception as e:
    print(f"Error during hashing: {e}")
    sys.exit(1)
