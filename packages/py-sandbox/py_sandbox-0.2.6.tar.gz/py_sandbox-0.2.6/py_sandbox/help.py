"""
py-sandbox help module
Mathematical computation sandbox - module discovery
"""

MODULES = {
    "sandbox": "Secure execution environment for mathematical expressions",
    "remote": "Dynamic module loading from remote sources",
    "cache": "Local caching for computational results",
    "verify": "Integrity verification for loaded modules",
    "help": "Module discovery and documentation"
}

REPO = "https://github.com/phanes19122025-cmyk/phi-linux"
PYPI = "https://pypi.org/project/py-sandbox/"

def list_modules():
    """List all available modules"""
    print("\n=== py-sandbox modules ===")
    for name, desc in MODULES.items():
        print(f"  {name}: {desc}")
    print(f"\nSource: {REPO}")
    print(f"PyPI: {PYPI}")
    return MODULES

def info():
    """Show package info"""
    return {
        "name": "py-sandbox",
        "modules": list(MODULES.keys()),
        "repo": REPO,
        "pypi": PYPI
    }

if __name__ == "__main__":
    list_modules()
