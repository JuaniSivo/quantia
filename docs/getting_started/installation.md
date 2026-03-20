# Installation

## Requirements

- Python 3.11 or later
- No external dependencies (pure standard library)

## Install from PyPI
```bash
pip install quantia
```

## Verify
```python
import quantia as qu
qu.Q(1.0, 'km').to('m')
# UnitFloat(1000.0, 'm')
```

## Install with documentation dependencies

If you want to build the documentation locally:
```bash
pip install "quantia[docs]"
```