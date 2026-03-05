# ==============================
# PROJECT: PassKey Logger
# FILE: file_manager.py
# PURPOSE: Clean structured I/O using user_data folder
# ==============================

import json
import base64
import os
from crypto_engine import encrypt_data, decrypt_data

HEADER_MAGIC = b"PKLOG001"

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))

USER_DATA_FOLDER = os.path.join(PROJECT_ROOT, "user_data")
INPUT_FOLDER = os.path.join(USER_DATA_FOLDER, "input_files")
OUTPUT_FOLDER = os.path.join(USER_DATA_FOLDER, "output_files")


def _ensure_folders():
    os.makedirs(INPUT_FOLDER, exist_ok=True)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def _b64e(b: bytes) -> str:
    return base64.b64encode(b).decode("ascii")


def _b64d(s: str) -> bytes:
    return base64.b64decode(s.encode("ascii"))


def encrypt_file(filename: str, passkey: bytes) -> None:
    """
    Encrypt file from user_data/input_files
    Save encrypted file as filename.pklog (no double extension)
    """
    _ensure_folders()

    input_path = os.path.join(INPUT_FOLDER, filename)

    if not os.path.exists(input_path):
        raise Exception(f"File not found in user_data/input_files: {filename}")

    with open(input_path, "rb") as f:
        data = f.read()

    salt, nonce, ciphertext = encrypt_data(passkey, data)

    name, ext = os.path.splitext(filename)

    metadata = {
        "version": 1,
        "orig_name": name,
        "orig_ext": ext,
        "salt_b64": _b64e(salt),
        "nonce_b64": _b64e(nonce),
    }

    meta_bytes = json.dumps(metadata).encode("utf-8")
    meta_len = len(meta_bytes).to_bytes(4, "big")

    encrypted_filename = f"{name}.pklog"
    output_path = os.path.join(OUTPUT_FOLDER, encrypted_filename)

    with open(output_path, "wb") as out:
        out.write(HEADER_MAGIC)
        out.write(meta_len)
        out.write(meta_bytes)
        out.write(ciphertext)

    print(f"[OK] Encrypted file saved to: {output_path}")


def decrypt_file(encrypted_filename: str, passkey: bytes, method: str) -> None:
    """
    Decrypt file from user_data/output_files
    Restore original extension automatically
    """
    _ensure_folders()

    encrypted_path = os.path.join(OUTPUT_FOLDER, encrypted_filename)

    if not os.path.exists(encrypted_path):
        raise Exception(f"Encrypted file not found in user_data/output_files: {encrypted_filename}")

    with open(encrypted_path, "rb") as f:
        blob = f.read()

    if blob[:8] != HEADER_MAGIC:
        raise Exception("Invalid PassKey Logger file.")

    meta_len = int.from_bytes(blob[8:12], "big")
    meta_start = 12
    meta_end = meta_start + meta_len

    metadata = json.loads(blob[meta_start:meta_end].decode())

    salt = _b64d(metadata["salt_b64"])
    nonce = _b64d(metadata["nonce_b64"])

    original_name = metadata["orig_name"]
    original_ext = metadata["orig_ext"]

    ciphertext = blob[meta_end:]
    plaintext = decrypt_data(passkey, salt, nonce, ciphertext)

    if method == "usb":
        output_name = f"{original_name}_out_usb{original_ext}"
    elif method == "qr":
        output_name = f"{original_name}_out_qr{original_ext}"
    else:
        raise Exception("Invalid decryption method.")

    output_path = os.path.join(OUTPUT_FOLDER, output_name)

    with open(output_path, "wb") as out:
        out.write(plaintext)

    print(f"[OK] Decrypted file saved to: {output_path}")