# ==============================
# PROJECT: PassKey Logger
# FILE: file_manager.py
# PURPOSE: Clean structured I/O using user_data folder
# ==============================

import json
import base64
import os
from pathlib import Path

from crypto_engine import encrypt_data, decrypt_data

HEADER_MAGIC = b"PKLOG001"

# Project root (…/PassKeyLogger)
BASE_DIR = Path(__file__).resolve().parent.parent

USER_DATA_DIR = BASE_DIR / "user_data"
INPUT_DIR = USER_DATA_DIR / "input_files"
OUTPUT_DIR = USER_DATA_DIR / "output_files"


def _ensure_folders():
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def _b64e(b: bytes) -> str:
    return base64.b64encode(b).decode("ascii")


def _b64d(s: str) -> bytes:
    return base64.b64decode(s.encode("ascii"))


def resolve_input_path(filename_or_path: str) -> Path:
    """
    Accept either a plain filename (e.g., 'test.txt') or a path
    (e.g., 'user_data/input_files/test.txt' or 'H:\\...\\test.txt').

    If a real path exists, use it.
    Otherwise treat it as a filename inside INPUT_DIR.
    """
    p = Path(filename_or_path)

    # If user gave a real path (absolute or relative) and it exists, use it
    if p.exists():
        return p

    # Otherwise treat it as a filename inside input_files
    candidate = INPUT_DIR / filename_or_path
    return candidate


def resolve_encrypted_path(filename_or_path: str) -> Path:
    """
    Same idea as resolve_input_path, but for encrypted files stored in OUTPUT_DIR.
    Accepts either 'file.pklog' or a full/relative path.
    """
    p = Path(filename_or_path)

    if p.exists():
        return p

    candidate = OUTPUT_DIR / filename_or_path
    return candidate


def encrypt_file(filename: str, passkey: bytes) -> None:
    """
    Encrypt file from user_data/input_files (or from a provided path).
    Save encrypted file as filename.pklog (no double extension).
    """
    _ensure_folders()

    input_path = resolve_input_path(filename)

    if not input_path.exists():
        raise Exception(f"File not found in user_data/input_files: {input_path}")

    with open(input_path, "rb") as f:
        data = f.read()

    salt, nonce, ciphertext = encrypt_data(passkey, data)

    # Use only the selected file name for output naming
    name, ext = os.path.splitext(input_path.name)

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
    output_path = OUTPUT_DIR / encrypted_filename

    with open(output_path, "wb") as out:
        out.write(HEADER_MAGIC)
        out.write(meta_len)
        out.write(meta_bytes)
        out.write(ciphertext)

    print(f"[OK] Encrypted file saved to: {output_path}")


def decrypt_file(encrypted_filename: str, passkey: bytes, method: str) -> None:
    """
    Decrypt file from user_data/output_files (or from a provided path).
    Restore original extension automatically.
    """
    _ensure_folders()

    encrypted_path = resolve_encrypted_path(encrypted_filename)

    if not encrypted_path.exists():
        raise Exception(f"Encrypted file not found in user_data/output_files: {encrypted_path}")

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

    output_path = OUTPUT_DIR / output_name

    with open(output_path, "wb") as out:
        out.write(plaintext)

    print(f"[OK] Decrypted file saved to: {output_path}")