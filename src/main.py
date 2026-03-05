# ==============================
# PassKey Logger
# Auto-create USB key if missing
# ==============================

import argparse
import sys
import os
import string

from file_manager import encrypt_file, decrypt_file
from usb_handler import find_usb_key_windows
from qr_handler import generate_qr_from_key, scan_qr_from_webcam
from key_handler import generate_key_to_path, read_key_from_path


# ------------------------------
# Detect USB Drive Letter
# ------------------------------

def find_usb_drive():
    drives = [f"{d}:\\" for d in string.ascii_uppercase if os.path.exists(f"{d}:\\")]

    for drive in drives:
        # Skip system drive (usually C:)
        if drive.upper().startswith("C"):
            continue
        return drive

    return None


# ------------------------------
# Ensure Passkey Exists on USB
# ------------------------------

def ensure_passkey():
    try:
        key = find_usb_key_windows()
        print("[INFO] Existing USB passkey detected.")
        return key
    except:
        print("[INFO] No passkey found. Creating new passkey on USB...")

        usb_drive = find_usb_drive()
        if not usb_drive:
            raise Exception("No USB drive detected.")

        key_path = os.path.join(usb_drive, "passkey.key")

        generate_key_to_path(key_path)
        key = read_key_from_path(key_path)

        generate_qr_from_key(key)

        print("[INFO] New passkey created and QR generated.")
        return key


# ------------------------------
# Encrypt
# ------------------------------

def cmd_encrypt(args):
    key = ensure_passkey()
    encrypt_file(args.filename, key)


# ------------------------------
# Decrypt (Interactive)
# ------------------------------

def cmd_decrypt(args):
    print("\nChoose decryption method:")
    print("1) USB")
    print("2) QR")

    choice = input("Enter choice (1 or 2): ").strip()

    if choice == "1":
        key = find_usb_key_windows()
        decrypt_file(args.filename, key, method="usb")
        return

    if choice == "2":
        key = scan_qr_from_webcam()
        decrypt_file(args.filename, key, method="qr")
        return

    print("[ERROR] Invalid selection.")
    sys.exit(1)


# ------------------------------
# CLI
# ------------------------------

def main():
    parser = argparse.ArgumentParser(prog="pk")

    sub = parser.add_subparsers(dest="cmd", required=True)

    p_enc = sub.add_parser("encrypt")
    p_enc.add_argument("filename")
    p_enc.set_defaults(func=cmd_encrypt)

    p_dec = sub.add_parser("decrypt")
    p_dec.add_argument("filename")
    p_dec.set_defaults(func=cmd_decrypt)

    args = parser.parse_args()

    try:
        args.func(args)
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()