# ==============================
# PROJECT: PassKey Logger
# FILE: crypto_engine.py
# PURPOSE: scrypt KDF + AES-256-GCM encrypt/decrypt core
# ==============================

import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt


# Scrypt parameters (good coursework defaults)
SCRYPT_N = 2**14
SCRYPT_R = 8
SCRYPT_P = 1

SALT_LEN = 16
NONCE_LEN = 12
AES_KEY_LEN = 32  # AES-256


def derive_key(passkey: bytes, salt: bytes) -> bytes:
    """
    Derives a strong 32-byte AES key from the external passkey using scrypt.
    """
    kdf = Scrypt(
        salt=salt,
        length=AES_KEY_LEN,
        n=SCRYPT_N,
        r=SCRYPT_R,
        p=SCRYPT_P,
    )
    return kdf.derive(passkey)


def encrypt_data(passkey: bytes, data: bytes) -> tuple[bytes, bytes, bytes]:
    """
    Encrypts bytes using AES-256-GCM.
    Returns (salt, nonce, ciphertext_with_tag).
    """
    salt = os.urandom(SALT_LEN)
    nonce = os.urandom(NONCE_LEN)

    aes_key = derive_key(passkey, salt)
    aesgcm = AESGCM(aes_key)

    ciphertext = aesgcm.encrypt(nonce, data, None)
    return salt, nonce, ciphertext


def decrypt_data(passkey: bytes, salt: bytes, nonce: bytes, ciphertext: bytes) -> bytes:
    """
    Decrypts AES-256-GCM ciphertext (includes tag).
    """
    aes_key = derive_key(passkey, salt)
    aesgcm = AESGCM(aes_key)

    return aesgcm.decrypt(nonce, ciphertext, None)