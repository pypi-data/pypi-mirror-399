"""
T.O.N. (Table of Nines) - 37 temporal/harmonic nodes.

The Table of Nines provides 37 nodes (m ∈ [0, 36]) where:
    T.O.N.(m) = m × 0.027

Key relationships:
    - T.O.N. values range from 0 to 0.972 (36 × 0.027)
    - Repitan / T.O.N. ≈ Fine Structure related (1.371742112)
    - 729 = 81 × 9 = 27th T.O.N. base
    - Fine Structure = Repitan(1)² links 27 Repitans to 37 T.O.N.

Usage:
    >>> from ra_system.ton import TON, all_tons
    >>> t = TON.create(9)
    >>> print(t.value)  # 0.243
    >>> print(t.index)  # 9
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

# T.O.N. coefficient: 0.027 = 1/37.037... ≈ 27/1000
TON_COEFFICIENT = 0.027


def is_valid_ton_index(m: int) -> bool:
    """Check if a value is a valid T.O.N. index."""
    return isinstance(m, int) and 0 <= m <= 36


@dataclass(frozen=True, order=True)
class TON:
    """
    A validated T.O.N. (Table of Nines) node.

    Invariants:
        - Index is in range [0, 36]
        - Value = index × 0.027
        - I5: T.O.N.(m) = m × 0.027 for all m ∈ [0, 36]
    """

    _index: int

    # Class-level constants
    ZERO: ClassVar[TON]
    NINTH: ClassVar[TON]
    EIGHTEENTH: ClassVar[TON]
    TWENTY_SEVENTH: ClassVar[TON]
    MAX: ClassVar[TON]

    def __post_init__(self) -> None:
        if not is_valid_ton_index(self._index):
            raise ValueError(f"T.O.N. index must be in [0, 36], got {self._index}")

    @classmethod
    def create(cls, m: int) -> TON | None:
        """Create a new T.O.N. with validation."""
        if is_valid_ton_index(m):
            return cls(m)
        return None

    @property
    def index(self) -> int:
        """Get the index (0-36)."""
        return self._index

    @property
    def value(self) -> float:
        """Get the T.O.N. value (m × 0.027) - Invariant I5."""
        return self._index * TON_COEFFICIENT

    @property
    def is_repitan_aligned(self) -> bool:
        """Check if this T.O.N. aligns with a Repitan (every 1.37... T.O.N.)."""
        # Repitans are at 1/27, 2/27, ... 27/27
        # T.O.N. are at 0/37, 1/37, ... 36/37 (approx via 0.027)
        # Alignment occurs when index * 0.027 ≈ n/27 for integer n
        for n in range(1, 28):
            repitan_value = n / 27
            if abs(self.value - repitan_value) < 0.01:
                return True
        return False

    @property
    def aligned_repitan_index(self) -> int | None:
        """Get the index of the aligned Repitan, if any."""
        for n in range(1, 28):
            repitan_value = n / 27
            if abs(self.value - repitan_value) < 0.01:
                return n
        return None

    def next(self) -> TON:
        """Get the next T.O.N. (wraps from 36 to 0)."""
        return TON(0 if self._index == 36 else self._index + 1)

    def prev(self) -> TON:
        """Get the previous T.O.N. (wraps from 0 to 36)."""
        return TON(36 if self._index == 0 else self._index - 1)

    def distance(self, other: TON) -> int:
        """Calculate distance to another T.O.N. (max 18)."""
        d = abs(self._index - other._index)
        return min(d, 37 - d)


# Initialize class constants after class definition
TON.ZERO = TON(0)
TON.NINTH = TON(9)
TON.EIGHTEENTH = TON(18)
TON.TWENTY_SEVENTH = TON(27)
TON.MAX = TON(36)


def ton_from_value(value: float) -> TON:
    """Convert a value to nearest T.O.N."""
    m = round(value / TON_COEFFICIENT)
    m = max(0, min(36, m))
    return TON(m)


def all_tons() -> list[TON]:
    """Get all 37 T.O.N. values."""
    return [TON(i) for i in range(37)]


def verify_ton_invariant() -> bool:
    """Verify Invariant I5: T.O.N.(m) = m × 0.027 for all m ∈ [0, 36]."""
    return all(abs(t.value - t.index * TON_COEFFICIENT) < 1e-10 for t in all_tons())


def verify_ton_range_invariant() -> bool:
    """Verify T.O.N. values are in [0, 1)."""
    return all(0 <= t.value < 1 for t in all_tons())


def repitan_ton_ratio() -> float:
    """
    Calculate the Repitan to T.O.N. ratio.

    This relates to the Fine Structure constant:
        Repitan(1) / T.O.N.(1) = (1/27) / 0.027 = 1.371742112...
        Fine Structure ≈ Repitan(1)² = 0.001371742
    """
    return (1 / 27) / TON_COEFFICIENT
