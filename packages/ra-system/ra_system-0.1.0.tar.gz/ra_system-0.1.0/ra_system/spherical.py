"""
θ/φ/r coordinate functions for Ra System dimensional mapping.

Coordinate transforms:
- θ (theta): Semantic sector ← 27 Repitans
- φ (phi): Access sensitivity ← 6 RACs
- h (harmonic): Coherence depth ← 5 Omega formats
- r (radius): Emergence intensity ← Ankh-normalized scalar
"""

from dataclasses import dataclass
from typing import Final

from ra_system.constants import ANKH
from ra_system.omega import OmegaFormat, harmonic_from_omega
from ra_system.rac import RacLevel
from ra_system.repitans import Repitan


@dataclass(frozen=True)
class RaCoordinate:
    """A complete Ra coordinate in 4-dimensional space."""

    theta: Repitan
    """Semantic sector (1-27)"""

    phi: RacLevel
    """Access sensitivity (RAC1-RAC6)"""

    harmonic: OmegaFormat
    """Coherence depth (Red-Blue)"""

    radius: float
    """Ankh-normalized intensity [0,1]"""

    def __post_init__(self) -> None:
        if not (0 <= self.radius <= 1):
            raise ValueError(f"Radius must be in [0, 1], got {self.radius}")

    @classmethod
    def create(
        cls,
        theta: Repitan,
        phi: RacLevel,
        harmonic: OmegaFormat,
        radius: float,
    ) -> "RaCoordinate | None":
        """Create a validated RaCoordinate."""
        if 0 <= radius <= 1:
            return cls(theta, phi, harmonic, radius)
        return None

    def is_valid(self) -> bool:
        """Check if the coordinate is valid."""
        return 0 <= self.radius <= 1


def theta_from_repitan(r: Repitan) -> float:
    """Convert Repitan to theta angle in degrees (0-360)."""
    return r.theta


# Phi values for each RAC level (0-255 encoded)
_PHI_VALUES: Final[dict[RacLevel, int]] = {
    RacLevel.RAC1: 0,    # Least restrictive
    RacLevel.RAC2: 43,
    RacLevel.RAC3: 85,
    RacLevel.RAC4: 128,
    RacLevel.RAC5: 170,
    RacLevel.RAC6: 255,  # Most restrictive
}


def phi_from_rac(rac: RacLevel) -> int:
    """Convert RacLevel to phi value (0-255 encoded)."""
    return _PHI_VALUES[rac]


def rac_from_phi(phi: int) -> RacLevel:
    """Convert phi value (0-255) to RacLevel."""
    if phi < 22:
        return RacLevel.RAC1
    if phi < 64:
        return RacLevel.RAC2
    if phi < 107:
        return RacLevel.RAC3
    if phi < 149:
        return RacLevel.RAC4
    if phi < 213:
        return RacLevel.RAC5
    return RacLevel.RAC6


def normalize_radius(r: float) -> float:
    """
    Normalize a raw radius value to [0, 1] using Ankh.

    r_normalized = r_raw / Ankh
    """
    return max(0.0, min(1.0, r / ANKH))


def denormalize_radius(r: float) -> float:
    """
    Denormalize a radius value from [0, 1] to raw scale.

    r_raw = r_normalized × Ankh
    """
    return r * ANKH


def coordinate_distance(c1: RaCoordinate, c2: RaCoordinate) -> float:
    """
    Calculate weighted distance between two coordinates.

    Returns value in [0, 1] where 0 = identical, 1 = maximally different.
    """
    theta_dist = c1.theta.distance(c2.theta) / 13.5
    phi_dist = abs(phi_from_rac(c1.phi) - phi_from_rac(c2.phi)) / 255
    h_dist = abs(harmonic_from_omega(c1.harmonic) - harmonic_from_omega(c2.harmonic)) / 4
    r_dist = abs(c1.radius - c2.radius)

    # Weighted average (from spec: w_θ=0.3, w_φ=0.4, w_h=0.2, w_r=0.1)
    return 0.3 * theta_dist + 0.4 * phi_dist + 0.2 * h_dist + 0.1 * r_dist


def verify_omega_indices() -> bool:
    """Verify Invariant O4: Omega format indices are 0-4."""
    return (
        harmonic_from_omega(OmegaFormat.RED) == 0
        and harmonic_from_omega(OmegaFormat.BLUE) == 4
    )
