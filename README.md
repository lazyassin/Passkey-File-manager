# PassKey Logger 🔐

PassKey Logger is a hardware-assisted file encryption tool designed to
secure sensitive files using modern cryptographic techniques. The system
uses AES-256-GCM authenticated encryption and stores the encryption key
on a USB device to provide an additional physical security layer.

This project was developed as coursework for the **Practical Cryptography
(ST6051CEM)** module.

---

## Features

- AES-256-GCM authenticated encryption
- Hardware-based key storage using USB devices
- QR-code backup for key recovery
- Command-line interface
- Modular Python architecture
- Integrity verification using authentication tags

---

## System Architecture

The system follows a modular architecture consisting of multiple
components responsible for encryption, key management, file operations,
and hardware interaction.

Modules include:

- `main.py` – handles command-line input and coordinates operations
- `crypto_engine.py` – performs AES-256-GCM encryption and decryption
- `key_handler.py` – generates and manages encryption keys
- `usb_handler.py` – detects USB devices containing the key
- `file_manager.py` – manages file input and output
- `qr_handler.py` – handles QR code key backup functionality

---

## Installation

Clone the repository:

```bash
git clone https://github.com/Lazyassin/passkey-logger.git
cd passkey-logger
