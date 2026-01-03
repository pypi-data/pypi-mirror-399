"""SHA256 integrity verification.

Provides hash generation and verification for
code integrity checks.

Usage:
    from py_sandbox import verify
    
    hash = verify.sha256('code string')
    is_valid = verify.check('code string', expected_hash)
    signature = verify.sign('code', 'secret')
"""

import hashlib
import hmac
from typing import Optional


def sha256(data: str) -> str:
    """
    Generate SHA256 hash of string.
    
    Args:
        data: String to hash
    
    Returns:
        Hex digest of SHA256 hash
    """
    return hashlib.sha256(data.encode('utf-8')).hexdigest()


def md5(data: str) -> str:
    """
    Generate MD5 hash (for compatibility, not security).
    
    Args:
        data: String to hash
    
    Returns:
        Hex digest of MD5 hash
    """
    return hashlib.md5(data.encode('utf-8')).hexdigest()


def check(data: str, expected_hash: str) -> bool:
    """
    Verify data matches expected hash.
    
    Args:
        data: String to verify
        expected_hash: Expected SHA256 hex digest
    
    Returns:
        True if hash matches
    """
    actual = sha256(data)
    # Constant-time comparison
    return hmac.compare_digest(actual, expected_hash.lower())


def sign(data: str, secret: str) -> str:
    """
    Create HMAC-SHA256 signature.
    
    Args:
        data: Data to sign
        secret: Secret key
    
    Returns:
        Hex digest of HMAC signature
    """
    return hmac.new(
        secret.encode('utf-8'),
        data.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()


def verify_signature(data: str, signature: str, secret: str) -> bool:
    """
    Verify HMAC-SHA256 signature.
    
    Args:
        data: Original data
        signature: Signature to verify
        secret: Secret key
    
    Returns:
        True if signature is valid
    """
    expected = sign(data, secret)
    return hmac.compare_digest(expected, signature.lower())