"""
OmegaFormat enum with conversion functions.

Five-level Omega format system for frequency/precision tiers.
Hierarchy: Red > Omega Major > Green > Omega Minor > Blue

Conversions use the Omega Ratio (Q-Ratio): Ω = 1.005662978
"""

from enum import IntEnum
from typing import Final


class OmegaFormat(IntEnum):
    """The five Omega format levels (coherence depth tiers)."""

    RED = 0
    OMEGA_MAJOR = 1
    GREEN = 2
    OMEGA_MINOR = 3
    BLUE = 4


def all_omega_formats() -> list[OmegaFormat]:
    """Get all Omega formats in order."""
    return list(OmegaFormat)


def omega_from_harmonic(h: int) -> OmegaFormat | None:
    """Get format from harmonic index (0-4)."""
    try:
        return OmegaFormat(h)
    except ValueError:
        return None


def harmonic_from_omega(fmt: OmegaFormat) -> int:
    """Get harmonic index (0-4) from format."""
    return int(fmt)


# Conversion factors matrix
_CONVERSION_FACTORS: Final[dict[OmegaFormat, dict[OmegaFormat, float]]] = {
    OmegaFormat.RED: {
        OmegaFormat.RED: 1.0,
        OmegaFormat.OMEGA_MAJOR: 0.994718414,
        OmegaFormat.GREEN: 1.000351482,
        OmegaFormat.OMEGA_MINOR: 1.006016451,
        OmegaFormat.BLUE: 1.000703088,
    },
    OmegaFormat.OMEGA_MAJOR: {
        OmegaFormat.RED: 1.005309630,
        OmegaFormat.OMEGA_MAJOR: 1.0,
        OmegaFormat.GREEN: 1.005662978,     # Ω
        OmegaFormat.OMEGA_MINOR: 1.011358026,
        OmegaFormat.BLUE: 1.006016451,
    },
    OmegaFormat.GREEN: {
        OmegaFormat.RED: 0.999648641,
        OmegaFormat.OMEGA_MAJOR: 0.994368911,     # 1/Ω
        OmegaFormat.GREEN: 1.0,
        OmegaFormat.OMEGA_MINOR: 1.005662978,     # Ω
        OmegaFormat.BLUE: 1.000351482,
    },
    OmegaFormat.OMEGA_MINOR: {
        OmegaFormat.RED: 0.994019530,
        OmegaFormat.OMEGA_MAJOR: 0.988769530,
        OmegaFormat.GREEN: 0.994368911,     # 1/Ω
        OmegaFormat.OMEGA_MINOR: 1.0,
        OmegaFormat.BLUE: 0.994718414,
    },
    OmegaFormat.BLUE: {
        OmegaFormat.RED: 0.999297406,
        OmegaFormat.OMEGA_MAJOR: 0.994019530,
        OmegaFormat.GREEN: 0.999648641,
        OmegaFormat.OMEGA_MINOR: 1.005309630,
        OmegaFormat.BLUE: 1.0,
    },
}


def convert_omega(from_fmt: OmegaFormat, to_fmt: OmegaFormat, x: float) -> float:
    """Convert a value between two Omega formats."""
    return x * _CONVERSION_FACTORS[from_fmt][to_fmt]


def green_to_omega_major(x: float) -> float:
    """Green to Omega Major: x / Ω."""
    return convert_omega(OmegaFormat.GREEN, OmegaFormat.OMEGA_MAJOR, x)


def omega_major_to_green(x: float) -> float:
    """Omega Major to Green: x × Ω."""
    return convert_omega(OmegaFormat.OMEGA_MAJOR, OmegaFormat.GREEN, x)


def green_to_omega_minor(x: float) -> float:
    """Green to Omega Minor: x × Ω."""
    return convert_omega(OmegaFormat.GREEN, OmegaFormat.OMEGA_MINOR, x)


def omega_minor_to_green(x: float) -> float:
    """Omega Minor to Green: x / Ω."""
    return convert_omega(OmegaFormat.OMEGA_MINOR, OmegaFormat.GREEN, x)


def red_to_blue(x: float) -> float:
    """Red to Blue."""
    return convert_omega(OmegaFormat.RED, OmegaFormat.BLUE, x)


def blue_to_red(x: float) -> float:
    """Blue to Red."""
    return convert_omega(OmegaFormat.BLUE, OmegaFormat.RED, x)


ROUNDTRIP_TOLERANCE: Final[float] = 1e-6
"""Tolerance for roundtrip conversion verification (accounts for matrix approximations)."""


def verify_omega_roundtrip(from_fmt: OmegaFormat, to_fmt: OmegaFormat, x: float) -> bool:
    """Verify Invariant C1: roundtrip conversions preserve value."""
    roundtrip = convert_omega(to_fmt, from_fmt, convert_omega(from_fmt, to_fmt, x))
    return abs(roundtrip - x) < ROUNDTRIP_TOLERANCE


def verify_all_omega_roundtrips(x: float) -> bool:
    """Verify all omega roundtrips for a value."""
    return all(
        verify_omega_roundtrip(from_fmt, to_fmt, x)
        for from_fmt in all_omega_formats()
        for to_fmt in all_omega_formats()
    )


def verify_omega_range() -> bool:
    """Verify Invariant R4: Omega format index ∈ {0, 1, 2, 3, 4}."""
    return all(harmonic_from_omega(fmt) <= 4 for fmt in all_omega_formats())
