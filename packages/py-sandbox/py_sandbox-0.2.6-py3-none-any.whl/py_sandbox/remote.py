"""Remote module loading with authentication and automatic fallback.

This is the COURIER module - loads Φ-linux modules from multiple sources:
1. Primary: n8n endpoint (live, authenticated, updatable)
2. Fallback: PyPI phi-linux-modules (stable, always online)
3. Emergency: npm @phi/modules (if PyPI down - rare)

Usage:
    from py_sandbox import remote
    
    # Configure primary endpoint
    remote.configure(
        endpoint='https://n8n.activegroup.it/phi-linux',
        api_key='PHI-xxxxx'
    )
    
    # Load module (auto-fallback if primary fails)
    result = remote.load('heartbeat')
    print(result['source'])  # 'n8n' or 'pypi_fallback'

Environment Variables:
    PY_SANDBOX_ENDPOINT: Primary endpoint URL
    PY_SANDBOX_KEY: API key for authentication
    PY_SANDBOX_FALLBACK: Fallback package name (default: phi-linux-modules)
"""
import os
import sys
import tempfile
import importlib.util
import subprocess

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

from . import cache as _cache
from . import verify as _verify

__all__ = ['configure', 'load', 'fallback', 'status']

# Configuration store
_config = {
    'endpoint': os.getenv('PY_SANDBOX_ENDPOINT', ''),
    'api_key': os.getenv('PY_SANDBOX_KEY', ''),
    'timeout': 30,
    'use_cache': True,
    'cache_ttl': 3600,
    'fallback_package': os.getenv('PY_SANDBOX_FALLBACK', 'phi-linux-modules'),
}


def configure(endpoint=None, api_key=None, timeout=None, use_cache=None,
              cache_ttl=None, fallback_package=None):
    """Configure remote loading settings.
    
    Args:
        endpoint: Primary HTTP endpoint URL
        api_key: Bearer token for authentication
        timeout: Request timeout in seconds
        use_cache: Whether to cache loaded modules
        cache_ttl: Cache time-to-live in seconds
        fallback_package: PyPI package name for fallback
    """
    if endpoint is not None:
        _config['endpoint'] = endpoint
    if api_key is not None:
        _config['api_key'] = api_key
    if timeout is not None:
        _config['timeout'] = timeout
    if use_cache is not None:
        _config['use_cache'] = use_cache
    if cache_ttl is not None:
        _config['cache_ttl'] = cache_ttl
    if fallback_package is not None:
        _config['fallback_package'] = fallback_package


def load(module_name, expected_hash=None, use_fallback=True, **kwargs):
    """
    Load and execute a remote module with automatic fallback.
    
    This is the main courier function. It attempts to load a module from
    the primary endpoint first, then falls back to PyPI if that fails.
    
    Args:
        module_name: Name of module to load (e.g., 'heartbeat', 'sync')
        expected_hash: Optional SHA256 hash for integrity verification
        use_fallback: If True, try PyPI fallback on primary failure
        **kwargs: Arguments passed to module's main() function
    
    Returns:
        Result from module.main(**kwargs) or the module object
    
    Raises:
        ConnectionError: If all sources fail
        ValueError: If hash verification fails
    
    Flow:
        1. Try primary endpoint (n8n) - live, authenticated
        2. On failure + use_fallback: try PyPI package - stable
        3. Execute module.main(**kwargs) and return result
    """
    # Try primary endpoint
    try:
        return _load_from_endpoint(module_name, expected_hash, **kwargs)
    except Exception as primary_error:
        if not use_fallback:
            raise
        
        # Try PyPI fallback
        try:
            return _load_from_pypi(module_name, **kwargs)
        except Exception as fallback_error:
            raise ConnectionError(
                f"All sources failed.\n"
                f"  Primary ({_config['endpoint'] or 'not configured'}): {primary_error}\n"
                f"  Fallback (PyPI {_config['fallback_package']}): {fallback_error}"
            )


def _load_from_endpoint(module_name, expected_hash=None, **kwargs):
    """Load from primary HTTP endpoint (n8n)."""
    if not HAS_REQUESTS:
        raise ImportError('requests library required: pip install requests')
    
    if not _config['endpoint']:
        raise ValueError('No endpoint configured. Use configure() or set PY_SANDBOX_ENDPOINT')
    
    cache_key = f"{_config['endpoint']}:{module_name}"
    
    # Try cache first
    if _config['use_cache']:
        cached = _cache.get(cache_key)
        if cached:
            return _execute_code(cached, module_name, expected_hash, 'n8n_cached', **kwargs)
    
    # Fetch from remote endpoint
    headers = {'User-Agent': 'py-sandbox-courier/0.2.0'}
    if _config['api_key']:
        headers['Authorization'] = f"Bearer {_config['api_key']}"
    
    url = f"{_config['endpoint'].rstrip('/')}/{module_name}.py"
    resp = requests.get(url, headers=headers, timeout=_config['timeout'])
    resp.raise_for_status()
    code = resp.text
    
    # Cache the result
    if _config['use_cache']:
        _cache.set(cache_key, code, _config['cache_ttl'])
    
    return _execute_code(code, module_name, expected_hash, 'n8n', **kwargs)


def _load_from_pypi(module_name, **kwargs):
    """
    Fallback: load from PyPI package.
    
    Auto-installs the fallback package if not present.
    
    Expects package structure:
        phi-linux-modules/
            phi_linux_modules/
                heartbeat.py
                sync.py
                context.py
    """
    pkg = _config['fallback_package']
    pkg_module = pkg.replace('-', '_')
    
    # Try to import, install if missing
    try:
        fallback_pkg = importlib.import_module(pkg_module)
    except ImportError:
        # Auto-install fallback package
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install',
            '--quiet', '--break-system-packages', pkg
        ], stderr=subprocess.DEVNULL)
        fallback_pkg = importlib.import_module(pkg_module)
    
    # Import the specific module
    full_module_name = f"{pkg_module}.{module_name}"
    module = importlib.import_module(full_module_name)
    
    if hasattr(module, 'main'):
        result = module.main(**kwargs)
        # Tag the source
        if isinstance(result, dict):
            result['source'] = 'pypi_fallback'
        return result
    return module


def _execute_code(code, module_name, expected_hash=None, source='unknown', **kwargs):
    """Execute code string as a Python module."""
    # Verify hash if provided
    if expected_hash and not _verify.check(code, expected_hash):
        raise ValueError(f'Hash verification failed for {module_name}')
    
    # Write to temp file and import
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_path = f.name
    
    try:
        spec = importlib.util.spec_from_file_location(module_name, temp_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        
        if hasattr(module, 'main'):
            result = module.main(**kwargs)
            # Tag the source
            if isinstance(result, dict):
                result['source'] = source
            return result
        return module
    finally:
        os.unlink(temp_path)


def fallback(module_name, endpoints, **kwargs):
    """
    Try multiple endpoints in order, use first that responds.
    
    Args:
        module_name: Module to load
        endpoints: List of (endpoint_url, api_key) tuples
        **kwargs: Arguments for module.main()
    
    Returns:
        Result from first successful endpoint, or PyPI fallback
    """
    errors = []
    
    for endpoint, api_key in endpoints:
        try:
            configure(endpoint=endpoint, api_key=api_key)
            return load(module_name, use_fallback=False, **kwargs)
        except Exception as e:
            errors.append((endpoint, str(e)))
    
    # All custom endpoints failed, try PyPI
    try:
        return _load_from_pypi(module_name, **kwargs)
    except Exception as e:
        errors.append(('pypi_fallback', str(e)))
    
    raise ConnectionError(f'All sources failed: {errors}')


def status():
    """
    Check connectivity to all configured sources.
    
    Returns:
        dict with status of primary and fallback sources
    """
    result = {
        'primary': None,
        'fallback': None,
        'config': {
            'endpoint': _config['endpoint'] or '(not configured)',
            'fallback_package': _config['fallback_package'],
        }
    }
    
    # Check primary endpoint
    if _config['endpoint'] and HAS_REQUESTS:
        try:
            headers = {'User-Agent': 'py-sandbox-courier/0.2.0'}
            if _config['api_key']:
                headers['Authorization'] = f"Bearer {_config['api_key']}"
            resp = requests.head(_config['endpoint'], headers=headers, timeout=5)
            result['primary'] = {
                'ok': resp.status_code < 400,
                'status_code': resp.status_code
            }
        except Exception as e:
            result['primary'] = {'ok': False, 'error': str(e)}
    elif not HAS_REQUESTS:
        result['primary'] = {'ok': False, 'error': 'requests not installed'}
    
    # Check fallback package availability
    pkg_module = _config['fallback_package'].replace('-', '_')
    try:
        importlib.import_module(pkg_module)
        result['fallback'] = {'ok': True, 'installed': True}
    except ImportError:
        result['fallback'] = {
            'ok': True,
            'installed': False,
            'note': 'Will auto-install on first use'
        }
    
    return result
