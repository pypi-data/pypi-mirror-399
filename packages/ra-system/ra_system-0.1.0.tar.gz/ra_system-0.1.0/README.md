# Ra System - Python Bindings

Type-safe Python bindings for the Ra System mathematical constants from "The Rods of Amon Ra" by Wesley H. Bateman.

## Installation

```bash
pip install ra-system
```

## Usage

```python
from ra_system import ANKH, Repitan, RacLevel, OmegaFormat
from ra_system.gates import access_level

# Check access at 80% coherence for RAC1
result = access_level(0.8, RacLevel.RAC1)
print(result.is_full_access)  # True

# Create a validated Repitan
r = Repitan.create(9)
print(r.value)  # 0.333...
```

## Features

- **Constants**: Ankh, Hunab, H-Bar, Omega, chromatic Pi/Phi variants
- **Repitans**: 27 semantic sectors with smart constructor validation
- **RAC Levels**: 6 access sensitivity levels with ordering invariants
- **Omega Formats**: 5 coherence depth tiers with conversion matrix
- **Spherical Coordinates**: θ/φ/h/r dimensional mapping
- **Access Gating**: Coherence-based access logic

## License

Apache-2.0
