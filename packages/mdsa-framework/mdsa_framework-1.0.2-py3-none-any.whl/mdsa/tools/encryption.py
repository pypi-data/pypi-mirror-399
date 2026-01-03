"""
Secure encryption utilities for tool API keys
Uses AES-256 encryption with a secret key
"""

import os
import hashlib
from cryptography.fernet import Fernet
from typing import Optional


class ToolEncryption:
    """Handle encryption/decryption of sensitive tool data (API keys)"""

    def __init__(self, secret_key: Optional[str] = None):
        """
        Initialize encryption with a secret key.

        Args:
            secret_key: Optional secret key. If not provided, uses environment variable.
        """
        # Get secret key from environment or use default (should be changed in production)
        key = secret_key or os.getenv('MDSA_ENCRYPTION_KEY', 'mdsa-tool-encryption-secret-change-in-production')

        # Generate Fernet key from secret
        # Hash the secret to get a consistent 32-byte key
        hashed = hashlib.sha256(key.encode()).digest()
        # Fernet requires base64-encoded 32-byte key
        import base64
        self.fernet_key = base64.urlsafe_b64encode(hashed)
        self.cipher = Fernet(self.fernet_key)

    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt a plaintext string (e.g., API key).

        Args:
            plaintext: The plaintext to encrypt

        Returns:
            Encrypted string (base64-encoded)
        """
        if not plaintext:
            return ""

        encrypted = self.cipher.encrypt(plaintext.encode())
        return encrypted.decode()

    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypt an encrypted string.

        Args:
            ciphertext: The encrypted string

        Returns:
            Decrypted plaintext
        """
        if not ciphertext:
            return ""

        try:
            decrypted = self.cipher.decrypt(ciphertext.encode())
            return decrypted.decode()
        except Exception as e:
            raise ValueError(f"Decryption failed: {e}")

    def is_encrypted(self, text: str) -> bool:
        """
        Check if a string appears to be encrypted.

        Args:
            text: String to check

        Returns:
            True if encrypted, False otherwise
        """
        try:
            # Try to decrypt - if it works, it's encrypted
            self.decrypt(text)
            return True
        except:
            return False


# Global encryption instance
_encryption_instance: Optional[ToolEncryption] = None


def get_encryption() -> ToolEncryption:
    """Get the global encryption instance."""
    global _encryption_instance
    if _encryption_instance is None:
        _encryption_instance = ToolEncryption()
    return _encryption_instance


def encrypt_api_key(api_key: str) -> str:
    """
    Encrypt an API key.

    Args:
        api_key: The API key to encrypt

    Returns:
        Encrypted API key
    """
    return get_encryption().encrypt(api_key)


def decrypt_api_key(encrypted_key: str) -> str:
    """
    Decrypt an API key.

    Args:
        encrypted_key: The encrypted API key

    Returns:
        Decrypted API key
    """
    return get_encryption().decrypt(encrypted_key)
