# AeTxt - Advanced Encrypted Text Editor

**AeTxt** is a modern, secure text editor designed for privacy-conscious users. It features strong AES-256 encryption, a stealth typing mode for public environments, and a sleek user interface.

![AeTxt Logo](logo.png)

## Features

### 🔒 Security First
*   **AES-GCM Encryption**: All files are encrypted using AES-256 in GCM mode. Each save generates a unique salt and nonce.
*   **Secure Password Derivation**: Keys are derived using PBKDF2HMAC (SHA256).
*   **Stealth Mode**: Type securely in public! Toggling this mode obfuscates characters visually while keeping the real content safe in memory.
*   **Panic Button**: Press **Alt + Alt** (Double Tap) to instantly Hide/Encrypt the view. If no password is set, it switches to Stealth Mode.

### 🎨 Modern Interface
*   **Dark & Light Themes**: Comfortable editing in any lighting condition.
*   **Zoomable Editor**: `Ctrl + MouseWheel` support.
*   **Markdown Preview**: Toggle a read-only Markdown preview with `Ctrl+M`.
*   **Context Menu**: Right-click in Windows Explorer -> "New" -> "AeTxt Encrypted File".

## Installation

### From Installer
Download the latest `.msi` installer from the releases page.

### From Source
1.  **Clone the repository**:
    ```bash
    git clone https://github.com/enderonat/aetxt.git
    cd aetxt
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the application**:
    ```bash
    python main.py
    ```

## Building the Installer

You can build the standalone MSI installer using `cx_Freeze`.

```bash
python setup_msi.py bdist_msi
```

The installer will be generated in the `dist/` directory.

## File Structure

*   `main.py`: Main application entry point and UI logic.
*   `crypto_handler.py`: Encryption and decryption logic.
*   `setup_msi.py`: Build script for the MSI installer.

## License

MIT
