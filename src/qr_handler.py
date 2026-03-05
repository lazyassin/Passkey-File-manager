# ==============================
# PROJECT: PassKey Logger
# FILE: qr_handler.py
# PURPOSE: Generate QR to user_data/qr_codes + scan from webcam
# ==============================

import base64
import os
import cv2
import qrcode
from pyzbar.pyzbar import decode

# Project root: PassKeyLogger/
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))

QR_FOLDER = os.path.join(PROJECT_ROOT, "user_data", "qr_codes")
QR_FILENAME = "passkey_qr.png"


def _ensure_qr_folder():
    os.makedirs(QR_FOLDER, exist_ok=True)


def generate_qr_from_key(key: bytes) -> None:
    """
    Saves a QR image containing base64(passkey) to:
      user_data/qr_codes/passkey_qr.png
    """
    _ensure_qr_folder()

    key_b64 = base64.b64encode(key).decode("ascii")
    img = qrcode.make(key_b64)

    output_path = os.path.join(QR_FOLDER, QR_FILENAME)
    img.save(output_path)

    print(f"[OK] QR generated at: {output_path}")
    print("     Scan it with your phone and SAVE it (screenshot recommended).")


def scan_qr_from_webcam() -> bytes:
    """
    Opens webcam and scans until QR is found.
    Returns decoded 32-byte passkey.
    """
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise Exception("Unable to access webcam (camera index 0).")

    print("Show QR to webcam. Press 'q' to cancel.")

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        decoded_objects = decode(frame)
        for obj in decoded_objects:
            payload = obj.data.decode("ascii").strip()

            cap.release()
            cv2.destroyAllWindows()

            try:
                key = base64.b64decode(payload.encode("ascii"))
            except Exception:
                raise Exception("QR payload is not valid base64.")

            if len(key) != 32:
                raise Exception(f"Invalid key length from QR (expected 32, got {len(key)}).")

            print("[OK] QR detected and key extracted.")
            return key

        cv2.imshow("PassKey Logger - QR Scanner (press q to cancel)", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    raise Exception("QR scan cancelled or failed.")