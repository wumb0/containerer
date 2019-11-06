from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.backends import default_backend as crypto_default_backend

def generate_keypair():
    key = ec.generate_private_key(backend=crypto_default_backend(), curve=ec.SECP521R1)
    privkey = key.private_bytes(crypto_serialization.Encoding.PEM, crypto_serialization.PrivateFormat.PKCS8, crypto_serialization.NoEncryption())
    pubkey = key.public_key().public_bytes(crypto_serialization.Encoding.OpenSSH, crypto_serialization.PublicFormat.OpenSSH)
    return privkey, pubkey
