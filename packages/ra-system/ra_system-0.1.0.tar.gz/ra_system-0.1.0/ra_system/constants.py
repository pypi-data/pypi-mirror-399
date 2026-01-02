"""
Ra System fundamental constants with type-safe wrappers.

All constants are derived from "The Rods of Amon Ra" by Wesley H. Bateman.
"""

from dataclasses import dataclass
from typing import Final

# Fundamental constants
ANKH: Final[float] = 5.08938
"""Ankh: Master harmonic constant = 5.08938"""

HUNAB: Final[float] = 1.05946
"""Hunab: Natural constant = 1.05946 (12th root of 2)"""

H_BAR: Final[float] = 1.05346545
"""H-Bar: Hunab / Omega = 1.05346545"""

OMEGA: Final[float] = 1.005662978
"""Omega Ratio (Q-Ratio): 1.005662978"""

FINE_STRUCTURE: Final[float] = 0.0013717421
"""Fine Structure: Repitan(1)² = 0.0013717421"""

# Pi variants (chromatic)
RED_PI: Final[float] = 3.14159265
"""Red Pi: Standard π = 3.14159265"""

GREEN_PI: Final[float] = 3.14754099
"""Green Pi: 3.14754099"""

BLUE_PI: Final[float] = 3.15349386
"""Blue Pi: 3.15349386"""

# Phi variants (chromatic)
RED_PHI: Final[float] = 1.614
"""Red Phi: 1.614"""

GREEN_PHI: Final[float] = 1.62
"""Green Phi: φ = 1.62"""

BLUE_PHI: Final[float] = 1.626
"""Blue Phi: 1.626"""


@dataclass(frozen=True)
class AnkhValue:
    """Typed wrapper for Ankh values."""

    value: float = ANKH

    def derive_rac1(self) -> float:
        """Derive RAC1 from Ankh (Invariant I2: RAC1 = Ankh / 8)."""
        return self.value / 8


@dataclass(frozen=True)
class OmegaRatio:
    """Typed wrapper for Omega Ratio."""

    value: float = OMEGA

    def reciprocal(self) -> float:
        """Get the reciprocal."""
        return 1 / self.value


def verify_ankh_invariant() -> bool:
    """Verify Invariant I1: Ankh = π_red × φ_green."""
    computed = RED_PI * GREEN_PHI
    return abs(ANKH - computed) < 0.0001


def verify_rac1_invariant(rac1_value: float) -> bool:
    """Verify Invariant I2: RAC1 = Ankh / 8."""
    computed = ANKH / 8
    return abs(rac1_value - computed) < 0.0001


def verify_hbar_invariant() -> bool:
    """Verify Invariant I3: H-Bar = Hunab / Ω."""
    computed = HUNAB / OMEGA
    return abs(H_BAR - computed) < 0.0001


def verify_fine_structure_invariant() -> bool:
    """Verify Invariant I6: Fine Structure = Repitan(1)² = (1/27)²."""
    r1 = 1 / 27
    return abs(FINE_STRUCTURE - r1 * r1) < 1e-10
