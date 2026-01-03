"""
py-sandbox: Secure sandbox for symbolic computation and numerical experiments
"""

from . import sandbox
from . import remote
from . import cache
from . import verify
from . import help

__version__ = "0.2.6"
__all__ = ["sandbox", "remote", "cache", "verify", "help"]

def modules():
    """Quick access to module list"""
    return help.list_modules()
