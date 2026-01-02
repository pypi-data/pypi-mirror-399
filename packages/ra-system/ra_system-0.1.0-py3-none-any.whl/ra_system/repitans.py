"""
Repitan type with smart constructor validating range [1, 27].

Repitans represent the 27 semantic sectors of the Ra System.
Each Repitan(n) = n/27 for n ∈ [1, 27].
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import ClassVar


def is_valid_repitan_index(n: int) -> bool:
    """Check if a value is a valid Repitan index."""
    return isinstance(n, int) and 1 <= n <= 27


@dataclass(frozen=True, order=True)
class Repitan:
    """
    A validated Repitan (semantic sector index).

    Invariants:
        - Index is in range [1, 27]
        - Value = index / 27
        - O3: 0 < Repitan(n) ≤ 1 for all n
    """

    _index: int

    # Class-level constants
    FIRST: ClassVar[Repitan]
    NINTH: ClassVar[Repitan]
    UNITY: ClassVar[Repitan]

    def __post_init__(self) -> None:
        if not is_valid_repitan_index(self._index):
            raise ValueError(f"Repitan index must be in [1, 27], got {self._index}")

    @classmethod
    def create(cls, n: int) -> Repitan | None:
        """Create a new Repitan with validation."""
        if is_valid_repitan_index(n):
            return cls(n)
        return None

    @property
    def index(self) -> int:
        """Get the index (1-27)."""
        return self._index

    @property
    def value(self) -> float:
        """Get the Repitan value (n/27) - Invariant I4."""
        return self._index / 27

    @property
    def theta(self) -> float:
        """Get theta angle in degrees (0-360)."""
        return self.value * 360

    @property
    def theta_radians(self) -> float:
        """Get theta angle in radians."""
        return self.value * 2 * math.pi

    def next(self) -> Repitan:
        """Get the next Repitan (wraps from 27 to 1)."""
        return Repitan(1 if self._index == 27 else self._index + 1)

    def prev(self) -> Repitan:
        """Get the previous Repitan (wraps from 1 to 27)."""
        return Repitan(27 if self._index == 1 else self._index - 1)

    def distance(self, other: Repitan) -> int:
        """Calculate angular distance to another Repitan (max 13)."""
        d = abs(self._index - other._index)
        return min(d, 27 - d)


# Initialize class constants after class definition
Repitan.FIRST = Repitan(1)
Repitan.NINTH = Repitan(9)
Repitan.UNITY = Repitan(27)


def repitan_from_theta(theta: float) -> Repitan:
    """Convert theta angle (degrees) to nearest Repitan."""
    normalized = (theta % 360) / 360
    n = round(normalized * 27)
    n = max(1, min(27, n if n != 0 else 27))
    return Repitan(n)


def all_repitans() -> list[Repitan]:
    """Get all 27 Repitans."""
    return [Repitan(i) for i in range(1, 28)]


def verify_repitan_invariant() -> bool:
    """Verify Invariant I4: Repitan(n) = n/27 for all n ∈ [1, 27]."""
    return all(abs(r.value - r.index / 27) < 1e-10 for r in all_repitans())


def verify_repitan_range_invariant() -> bool:
    """Verify Invariant O3: For all n: 0 < Repitan(n) ≤ 1."""
    return all(0 < r.value <= 1 for r in all_repitans())
