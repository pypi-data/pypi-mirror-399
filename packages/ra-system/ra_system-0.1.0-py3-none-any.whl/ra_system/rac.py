"""
RacLevel enum (RAC1..RAC6) with validation.

Resonant Access Constants (RACs) represent access sensitivity levels.
RAC1 is the highest (least restrictive), RAC6 is the lowest (most restrictive).

Invariant O1: RAC1 > RAC2 > RAC3 > RAC4 > RAC5 > RAC6 > 0
"""

from dataclasses import dataclass
from enum import IntEnum
from typing import Final

from ra_system.constants import ANKH


class RacLevel(IntEnum):
    """The six Resonant Access Constant levels."""

    RAC1 = 1
    RAC2 = 2
    RAC3 = 3
    RAC4 = 4
    RAC5 = 5
    RAC6 = 6


# RAC values in Red Rams
_RAC_VALUES: Final[dict[RacLevel, float]] = {
    RacLevel.RAC1: 0.6361725,      # Ankh / 8
    RacLevel.RAC2: 0.628318519,    # 2π/10 approximation
    RacLevel.RAC3: 0.57255525,     # φ × Hunab × 1/3
    RacLevel.RAC4: 0.523598765,    # π/6 approximation
    RacLevel.RAC5: 0.4580442,      # Ankh × 9 / 100
    RacLevel.RAC6: 0.3998594565,   # RAC lattice terminus
}

# RAC values in meters
_RAC_VALUES_METERS: Final[dict[RacLevel, float]] = {
    RacLevel.RAC1: 0.639591666,
    RacLevel.RAC2: 0.631695473,
    RacLevel.RAC3: 0.5756325,
    RacLevel.RAC4: 0.526412894,
    RacLevel.RAC5: 0.460506,
    RacLevel.RAC6: 0.4020085371,
}

# Pyramid divisions
_PYRAMID_DIVISIONS: Final[dict[RacLevel, float]] = {
    RacLevel.RAC1: 360.0,      # Circle degrees
    RacLevel.RAC2: 364.5,      # Balmer constant
    RacLevel.RAC3: 400.0,
    RacLevel.RAC4: 437.4,      # 27 × φ_green
    RacLevel.RAC5: 500.0,
    RacLevel.RAC6: 572.756493, # 1.125 × Green Ankh
}


@dataclass(frozen=True)
class RacValue:
    """RAC value in Red Rams (must be 0 < x < 1)."""

    value: float

    def __post_init__(self) -> None:
        if not (0 < self.value < 1):
            raise ValueError(f"RAC value must be in (0, 1), got {self.value}")


def all_rac_levels() -> list[RacLevel]:
    """Get all RAC levels in order."""
    return list(RacLevel)


def rac_from_level(n: int) -> RacLevel | None:
    """Get RacLevel from numeric level (1-6)."""
    try:
        return RacLevel(n)
    except ValueError:
        return None


def rac_value(level: RacLevel) -> float:
    """Get the RAC value in Red Rams for a given level."""
    return _RAC_VALUES[level]


def rac_value_meters(level: RacLevel) -> float:
    """Get the RAC value in meters for a given level."""
    return _RAC_VALUES_METERS[level]


def rac_value_normalized(level: RacLevel) -> float:
    """Get the RAC value normalized to RAC1 (RAC1 normalized = 1.0)."""
    return rac_value(level) / rac_value(RacLevel.RAC1)


def pyramid_division(level: RacLevel) -> float:
    """Get pyramid division for a RAC level."""
    return _PYRAMID_DIVISIONS[level]


def is_valid_rac_value(x: float) -> bool:
    """Check if a value is valid for a RAC (0 < x < 1)."""
    return 0 < x < 1


def verify_rac_ordering() -> bool:
    """Verify Invariant O1: RAC1 > RAC2 > RAC3 > RAC4 > RAC5 > RAC6 > 0."""
    values = [rac_value(level) for level in all_rac_levels()]
    # Check descending order
    for i in range(len(values) - 1):
        if values[i] <= values[i + 1]:
            return False
    # Check all positive
    return all(v > 0 for v in values)


def verify_rac_range() -> bool:
    """Verify Invariant R1: 0 < RAC(i) < 1 for all i ∈ [1, 6]."""
    return all(is_valid_rac_value(rac_value(level)) for level in all_rac_levels())


def verify_rac1_derivation() -> bool:
    """Verify Invariant I2: RAC1 = Ankh / 8."""
    computed = ANKH / 8
    return abs(rac_value(RacLevel.RAC1) - computed) < 0.0001
