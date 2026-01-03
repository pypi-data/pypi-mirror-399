"""Safe Python code execution with restricted builtins.

This module provides sandboxed execution of untrusted Python code
by restricting available builtins and blocking dangerous imports.

Usage:
    from py_sandbox import run, check
    
    result = run('x = 2 + 2')
    # {'x': 4, 'success': True}
    
    safe, reason = check('import os')
    # (False, 'Blocked import: os')
"""

import ast
import sys
from typing import Dict, Any, Tuple, Optional

# Restricted builtins - safe subset
SAFE_BUILTINS = {
    'abs': abs, 'all': all, 'any': any, 'ascii': ascii,
    'bin': bin, 'bool': bool, 'bytearray': bytearray,
    'bytes': bytes, 'callable': callable, 'chr': chr,
    'complex': complex, 'dict': dict, 'divmod': divmod,
    'enumerate': enumerate, 'filter': filter, 'float': float,
    'format': format, 'frozenset': frozenset, 'hash': hash,
    'hex': hex, 'int': int, 'isinstance': isinstance,
    'issubclass': issubclass, 'iter': iter, 'len': len,
    'list': list, 'map': map, 'max': max, 'min': min,
    'next': next, 'object': object, 'oct': oct, 'ord': ord,
    'pow': pow, 'print': print, 'range': range, 'repr': repr,
    'reversed': reversed, 'round': round, 'set': set,
    'slice': slice, 'sorted': sorted, 'str': str, 'sum': sum,
    'tuple': tuple, 'type': type, 'zip': zip,
    'True': True, 'False': False, 'None': None,
}

# Blocked imports - dangerous modules
BLOCKED_IMPORTS = {
    'os', 'sys', 'subprocess', 'shutil', 'pathlib',
    'socket', 'requests', 'urllib', 'http',
    'importlib', '__import__', 'builtins',
    'ctypes', 'multiprocessing', 'threading',
    'pickle', 'marshal', 'shelve',
    'code', 'codeop', 'compile',
}


class SandboxError(Exception):
    """Raised when sandbox execution fails."""
    pass


def check(code: str) -> Tuple[bool, str]:
    """
    Check if code is safe to execute.
    
    Args:
        code: Python code string to check
    
    Returns:
        Tuple of (is_safe, reason)
    """
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return False, f'Syntax error: {e}'
    
    for node in ast.walk(tree):
        # Check imports
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split('.')[0] in BLOCKED_IMPORTS:
                    return False, f'Blocked import: {alias.name}'
        
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.module.split('.')[0] in BLOCKED_IMPORTS:
                return False, f'Blocked import: {node.module}'
        
        # Check dangerous function calls
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                if node.func.id in ('exec', 'eval', 'compile', 'open'):
                    return False, f'Blocked function: {node.func.id}'
            elif isinstance(node.func, ast.Attribute):
                if node.func.attr in ('system', 'popen', 'spawn'):
                    return False, f'Blocked method: {node.func.attr}'
    
    return True, 'Code appears safe'


def run(code: str, 
        globals_dict: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None) -> Dict[str, Any]:
    """
    Execute code in a restricted sandbox.
    
    Args:
        code: Python code string to execute
        globals_dict: Optional additional globals to provide
        timeout: Optional execution timeout (not implemented)
    
    Returns:
        Dict with execution results and 'success' key
    
    Raises:
        SandboxError: If code fails safety check or execution
    """
    # Safety check first
    is_safe, reason = check(code)
    if not is_safe:
        raise SandboxError(reason)
    
    # Prepare execution environment
    exec_globals = {'__builtins__': SAFE_BUILTINS}
    if globals_dict:
        exec_globals.update(globals_dict)
    
    exec_locals = {}
    
    try:
        exec(code, exec_globals, exec_locals)
        
        # Return locals (excluding internal stuff)
        result = {
            k: v for k, v in exec_locals.items()
            if not k.startswith('_')
        }
        result['success'] = True
        return result
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__,
        }


def main(**kwargs) -> Dict[str, Any]:
    """Entry point for remote.load() compatibility."""
    code = kwargs.get('code', '')
    if not code:
        return {
            'success': False,
            'error': 'No code provided',
            'usage': "run(code='x = 1 + 1')"
        }
    return run(code)


if __name__ == '__main__':
    # Quick test
    import json
    result = run('x = 2 + 2\ny = x * 3')
    print(json.dumps(result, indent=2))