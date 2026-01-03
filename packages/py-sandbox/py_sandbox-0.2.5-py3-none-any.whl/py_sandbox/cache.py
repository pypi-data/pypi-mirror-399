"""Local file caching with TTL support.

Provides simple key-value caching to disk with
automatic expiration and cleanup.

Usage:
    from py_sandbox import cache
    
    cache.set('my_key', 'my_value', ttl=3600)  # 1 hour
    value = cache.get('my_key')
    cache.delete('my_key')
    cache.clear()
"""

import os
import json
import time
import hashlib
from typing import Any, Optional, Dict

# Cache directory
CACHE_DIR = os.path.expanduser('~/.py_sandbox_cache')
DEFAULT_TTL = 3600  # 1 hour


def _ensure_cache_dir():
    """Create cache directory if needed."""
    os.makedirs(CACHE_DIR, exist_ok=True)


def _key_to_path(key: str) -> str:
    """Convert key to safe file path."""
    # Hash key for safety
    key_hash = hashlib.sha256(key.encode()).hexdigest()[:16]
    return os.path.join(CACHE_DIR, f'{key_hash}.cache')


def get(key: str) -> Optional[Any]:
    """
    Get value from cache.
    
    Args:
        key: Cache key
    
    Returns:
        Cached value or None if not found/expired
    """
    path = _key_to_path(key)
    
    if not os.path.exists(path):
        return None
    
    try:
        with open(path) as f:
            data = json.load(f)
        
        # Check expiration
        if data.get('expires', 0) < time.time():
            os.unlink(path)
            return None
        
        return data.get('value')
    except (json.JSONDecodeError, OSError):
        return None


def set(key: str, value: Any, ttl: int = DEFAULT_TTL) -> bool:
    """
    Set value in cache.
    
    Args:
        key: Cache key
        value: Value to cache (must be JSON serializable)
        ttl: Time to live in seconds
    
    Returns:
        True if successful
    """
    _ensure_cache_dir()
    path = _key_to_path(key)
    
    data = {
        'key': key,
        'value': value,
        'created': time.time(),
        'expires': time.time() + ttl,
    }
    
    try:
        with open(path, 'w') as f:
            json.dump(data, f)
        return True
    except (TypeError, OSError):
        return False


def delete(key: str) -> bool:
    """
    Delete key from cache.
    
    Args:
        key: Cache key
    
    Returns:
        True if deleted, False if not found
    """
    path = _key_to_path(key)
    
    if os.path.exists(path):
        os.unlink(path)
        return True
    return False


def clear() -> int:
    """
    Clear all cached items.
    
    Returns:
        Number of items cleared
    """
    if not os.path.exists(CACHE_DIR):
        return 0
    
    count = 0
    for f in os.listdir(CACHE_DIR):
        if f.endswith('.cache'):
            os.unlink(os.path.join(CACHE_DIR, f))
            count += 1
    return count


def stats() -> Dict[str, Any]:
    """
    Get cache statistics.
    
    Returns:
        Dict with cache stats
    """
    if not os.path.exists(CACHE_DIR):
        return {'items': 0, 'size_bytes': 0, 'expired': 0}
    
    items = 0
    expired = 0
    size = 0
    
    for f in os.listdir(CACHE_DIR):
        if f.endswith('.cache'):
            path = os.path.join(CACHE_DIR, f)
            items += 1
            size += os.path.getsize(path)
            
            try:
                with open(path) as fp:
                    data = json.load(fp)
                if data.get('expires', 0) < time.time():
                    expired += 1
            except:
                pass
    
    return {
        'items': items,
        'size_bytes': size,
        'expired': expired,
        'cache_dir': CACHE_DIR,
    }