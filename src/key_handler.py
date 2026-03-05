# ==============================
# PROJECT: PassKey Logger
# FILE: key_handler.py
# PURPOSE: Generate + read external 32-byte passkey files
# ==============================

import os

KEY_LENGTH = 32
DEFAULT_KEY_FILENAME = "passkey.key"


def generate_key_to_path(path: str) -> None:
    """
    Generates a random 32-byte passkey and writes it to the given path.
    Intended to be stored on USB (or other external medium).
    """
    if os.path.exists(path):
        raise Exception(f"Key file already exists: {path}")

    key = os.urandom(KEY_LENGTH)

    with open(path, "wb") as f:
        f.write(key)

    print(f"[OK] Passkey created: {path}")


def read_key_from_path(path: str) -> bytes:
    """
    Reads the key from the given path. Must be exactly 32 bytes.
    """
    if not os.path.exists(path):
        raise Exception(f"Key file not found: {path}")

    with open(path, "rb") as f:
        key = f.read()

    if len(key) != KEY_LENGTH:
        raise Exception(f"Invalid key length. Expected {KEY_LENGTH} bytes, got {len(key)} bytes.")

    return key