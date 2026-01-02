"""
Security Module

Provides encryption and decryption interfaces.

Currently uses simple Base64 + XOR encryption as a placeholder implementation.
Production environments should replace with strong encryption algorithms like AES.
"""

import base64
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Default key
_DEFAULT_KEY = b"tspkg_default_key_change_in_production"


def _get_key(key: Optional[str] = None) -> bytes:
    """
    Get encryption key

    Args:
        key: Key string (optional), if None then use default key

    Returns:
        Key bytes
    """
    if key is None:
        # Try to get from environment variable
        import os
        env_key = os.getenv("TSPKG_ENCRYPTION_KEY")
        if env_key:
            return env_key.encode('utf-8')
        return _DEFAULT_KEY
    return key.encode('utf-8') if isinstance(key, str) else key


def encrypt(data: bytes, key: Optional[str] = None) -> bytes:
    """
    Encrypt data

    Current implementation: simple XOR + Base64 encoding

    Args:
        data: Byte data to encrypt
        key: Encryption key (optional), if None then use environment variable or default key

    Returns:
        Encrypted byte data (Base64 encoded)

    Example:
        encrypted = encrypt(b"hello world", "my_secret_key")
    """
    if not data:
        return b""

    encryption_key = _get_key(key)
    
    # Simple XOR encryption
    encrypted = bytearray()
    key_bytes = encryption_key
    for i, byte in enumerate(data):
        encrypted.append(byte ^ key_bytes[i % len(key_bytes)])
    
    # Base64 encoding
    encoded = base64.b64encode(bytes(encrypted))
    return encoded


def decrypt(data: bytes, key: Optional[str] = None) -> bytes:
    """
    Decrypt data

    Current implementation: Base64 decoding + XOR decryption

    Args:
        data: Byte data to decrypt (Base64 encoded)
        key: Decryption key (optional), if None then use environment variable or default key

    Returns:
        Decrypted byte data

    Raises:
        ValueError: If data format is incorrect

    Example:
        decrypted = decrypt(encrypted_data, "my_secret_key")
    """
    if not data:
        return b""

    try:
        # Base64 decoding
        decoded = base64.b64decode(data)
    except Exception as e:
        raise ValueError(f"Invalid base64 data: {e}")

    decryption_key = _get_key(key)
    
    # XOR decryption (XOR is symmetric, encryption and decryption use the same operation)
    decrypted = bytearray()
    key_bytes = decryption_key
    for i, byte in enumerate(decoded):
        decrypted.append(byte ^ key_bytes[i % len(key_bytes)])
    
    return bytes(decrypted)


def encrypt_file(file_path: str, output_path: Optional[str] = None, key: Optional[str] = None) -> str:
    """
    Encrypt file

    Args:
        file_path: Path of file to encrypt
        output_path: Output file path (optional), if None then overwrite original file
        key: Encryption key (optional)

    Returns:
        Output file path
    """
    with open(file_path, 'rb') as f:
        data = f.read()
    
    encrypted_data = encrypt(data, key)
    
    output = output_path or file_path
    with open(output, 'wb') as f:
        f.write(encrypted_data)
    
    return output


def decrypt_file(file_path: str, output_path: Optional[str] = None, key: Optional[str] = None) -> str:
    """
    Decrypt file

    Args:
        file_path: Path of file to decrypt
        output_path: Output file path (optional), if None then overwrite original file
        key: Decryption key (optional)

    Returns:
        Output file path

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file format is incorrect
    """
    with open(file_path, 'rb') as f:
        encrypted_data = f.read()
    
    decrypted_data = decrypt(encrypted_data, key)
    
    output = output_path or file_path
    with open(output, 'wb') as f:
        f.write(decrypted_data)
    
    return output

