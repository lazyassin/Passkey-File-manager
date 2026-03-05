# ==============================
# PassKey Logger
# Auto-create USB key if missing
# Menu mode + numbered file selection
# ==============================

import argparse
import sys
import os
import string
from pathlib import Path

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
    except Exception:
        print("[INFO] No passkey found. Creating new passkey on USB...")

        usb_drive = find_usb_drive()
        if not usb_drive:
            raise Exception("No USB drive detected.")

        key_path = os.path.join(usb_drive, "passkey.key")

        generate_key_to_path(key_path)
        key = read_key_from_path(key_path)

        # Optional: generate QR backup for recovery
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
# Decrypt (Interactive USB/QR)
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
# File Picker Helpers
# ------------------------------
def _collect_files(search_dirs, patterns=("*",)):
    """Return a sorted list of unique files (Path objects) in search_dirs matching patterns."""
    files = []
    for d in search_dirs:
        p = Path(d)
        if not p.exists() or not p.is_dir():
            continue
        for pat in patterns:
            files.extend([f for f in p.glob(pat) if f.is_file()])

    # Deduplicate by resolved full path
    uniq = {}
    for f in files:
        try:
            uniq[str(f.resolve())] = f
        except Exception:
            uniq[str(f)] = f

    return sorted(uniq.values(), key=lambda x: x.name.lower())


def _pick_file_from_list(files, prompt="Select a file number (or 0 to cancel): "):
    """Print numbered list and return selected Path or None."""
    if not files:
        print("[INFO] No files found.")
        return None

    print("\nAvailable files:")
    for i, f in enumerate(files, start=1):
        print(f"{i}) {f.name}")

    while True:
        choice = input(prompt).strip()
        if choice == "0":
            return None
        if choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(files):
                return files[idx - 1]
        print("[ERROR] Invalid selection. Enter a number from the list.")


# ------------------------------
# Menu (Interactive Mode)
# ------------------------------
def interactive_menu():
    while True:
        print("\n===================================")
        print(" PassKey Logger")
        print("===================================")
        print("1) Encrypt a file")
        print("2) Decrypt a file")
        print("0) Exit")

        choice = input("Select option: ").strip()

        if choice == "1":
            # Look for plaintext files (edit these folders if your project uses different paths)
            search_dirs = [
                "user_data/input_files",
                "user_data",
            ]
            files = _collect_files(search_dirs, patterns=("*",))
            picked = _pick_file_from_list(
                files, prompt="Select file to ENCRYPT (or 0 to cancel): "
            )

            if picked:
                class _Args:  # lightweight args object to reuse cmd_encrypt
                    pass

                args = _Args()
                args.filename = str(picked)  # full path
                try:
                    cmd_encrypt(args)
                except Exception as e:
                    print(f"[ERROR] {e}")

            input("\nPress Enter to return to menu...")

        elif choice == "2":
            # Look for encrypted files (default assumes *.pklog extension)
            search_dirs = [
                "user_data/output_files",
                "user_data",
            ]
            files = _collect_files(search_dirs, patterns=("*.pklog",))
            picked = _pick_file_from_list(
                files, prompt="Select file to DECRYPT (or 0 to cancel): "
            )

            if picked:
                class _Args:
                    pass

                args = _Args()
                args.filename = str(picked)
                try:
                    cmd_decrypt(args)
                except Exception as e:
                    print(f"[ERROR] {e}")

            input("\nPress Enter to return to menu...")

        elif choice == "0":
            print("Exiting PassKey Logger...")
            break

        else:
            print("Invalid option.")
            input("\nPress Enter to return to menu...")


# ------------------------------
# CLI
# ------------------------------
def main():
    # If no CLI args were provided, run the interactive menu
    if len(sys.argv) == 1:
        interactive_menu()
        return

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