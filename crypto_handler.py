import os
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

class CryptoHandler:
    def __init__(self):
        self.salt_size = 16
        self.nonce_size = 12
        self.iterations = 100000

    def _derive_key(self, password: str, salt: bytes) -> bytes:
        """Derives a 256-bit key from the password using PBKDF2."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=self.iterations,
        )
        return kdf.derive(password.encode('utf-8'))

    def encrypt(self, plain_text: str, password: str) -> bytes:
        """
        Encrypts text using AES-GCM.
        Returns bytes: salt + nonce + ciphertext + tag
        """
        salt = os.urandom(self.salt_size)
        key = self._derive_key(password, salt)
        aesgcm = AESGCM(key)
        nonce = os.urandom(self.nonce_size)
        
        data = plain_text.encode('utf-8')
        ciphertext = aesgcm.encrypt(nonce, data, None) # Tag is included in ciphertext by cryptography library
        
        return salt + nonce + ciphertext

    def decrypt(self, file_data: bytes, password: str) -> str:
        """
        Decrypts data using AES-GCM.
        Expects bytes: salt + nonce + ciphertext + tag
        """
        if len(file_data) < self.salt_size + self.nonce_size:
            raise ValueError("File corrupted or too short")

        salt = file_data[:self.salt_size]
        nonce = file_data[self.salt_size : self.salt_size + self.nonce_size]
        ciphertext = file_data[self.salt_size + self.nonce_size:]

        key = self._derive_key(password, salt)
        aesgcm = AESGCM(key)
        
        decrypted_data = aesgcm.decrypt(nonce, ciphertext, None)
        return decrypted_data.decode('utf-8')
