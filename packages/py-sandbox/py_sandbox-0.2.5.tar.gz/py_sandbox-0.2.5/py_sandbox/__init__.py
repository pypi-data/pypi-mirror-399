"""py-sandbox: Execute untrusted Python safely with remote loading.

Published on PyPI: https://pypi.org/project/py-sandbox/

Core modules:
- sandbox: Safe code execution with restricted builtins
- cache: Local file caching with TTL
- verify: SHA256 integrity verification
- remote: Remote module loading with automatic fallback

Usage:
    from py_sandbox import run, check
    
    # Execute untrusted code safely
    result = run('x = 2 + 2')
    print(result)  # {'x': 4, 'success': True}
    
    # Load remote modules with fallback
    from py_sandbox import remote
    remote.configure(endpoint='https://...', api_key='...')
    result = remote.load('heartbeat')
"""

__version__ = '0.2.0'
__author__ = 'Φ'

from .sandbox import run, check, SandboxError
from . import cache
from . import verify
from . import remote

__all__ = ['run', 'check', 'SandboxError', 'cache', 'verify', 'remote', '__version__']