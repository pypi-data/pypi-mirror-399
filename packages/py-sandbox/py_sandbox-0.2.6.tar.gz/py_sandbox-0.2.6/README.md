# py-sandbox

[![PyPI version](https://badge.fury.io/py/py-sandbox.svg)](https://pypi.org/project/py-sandbox/)

Secure sandbox for symbolic computation and numerical experiments.

## Installation

```bash
pip install py-sandbox
```

## Features

- **Symbolic computation sandbox** — Safe evaluation of mathematical expressions
- **Numerical experiment isolation** — Controlled environment for computational mathematics
- **Remote module loading** — Dynamic capability extension
- **Secure execution** — Sandboxed Python evaluation

## Quick Start

```python
from py_sandbox import sandbox, remote

# Initialize sandbox
sb = sandbox.Sandbox()

# Load remote mathematical modules
remote.load_module("advanced_math")

# Execute computations safely
result = sb.execute("integrate(x**2, x)")
```

## Use Cases

- Mathematical modeling experiments
- Symbolic algebra computations
- Numerical analysis in isolated environments
- Educational math sandboxes

## Requirements

- Python ≥3.8

## License

MIT

---
*Part of the Φ mathematical infrastructure*
