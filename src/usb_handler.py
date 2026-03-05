# ==============================
# PROJECT: PassKey Logger
# FILE: usb_handler.py
# PURPOSE: Windows USB auto-detection for passkey.key
# ==============================

import os
import string

KEY_FILENAME = "passkey.key"
KEY_LENGTH = 32


def find_usb_key_windows() -> bytes:
    """
    Scans all Windows drive letters (A: to Z:) for passkey.key.
    Returns the key bytes if found.
    """
    drives = [f"{d}:\\" for d in string.ascii_uppercase if os.path.exists(f"{d}:\\")]

    for drive in drives:
        candidate = os.path.join(drive, KEY_FILENAME)

        if os.path.isfile(candidate):
            with open(candidate, "rb") as f:
                key = f.read()

            if len(key) != KEY_LENGTH:
                raise Exception(f"Found {candidate} but key length is invalid ({len(key)} bytes).")

            print(f"[OK] Found USB passkey: {candidate}")
            return key

    raise Exception(f"No USB passkey found. Expected {KEY_FILENAME} on a removable drive.")