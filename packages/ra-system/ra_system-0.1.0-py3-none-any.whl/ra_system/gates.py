"""
AccessResult type + gating logic from spec Section 4.

Access gating determines whether a fragment/signal can emerge based on
coherence and consent levels.

From Section 4 of ra_integration_spec.md:

    AccessLevel(user_coherence, fragment_rac) → {FullAccess, PartialAccess(α), Blocked}

    threshold(R_f) = RAC(R_f) / RAC₁
    C_floor = φ_green / Ankh ≈ 0.3183
    C_ceiling = 1.0
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Final

from ra_system.constants import ANKH, GREEN_PHI
from ra_system.rac import RacLevel, rac_value_normalized
from ra_system.repitans import Repitan

COHERENCE_FLOOR: Final[float] = GREEN_PHI / ANKH
"""Coherence floor: φ_green / Ankh ≈ 0.3183"""

COHERENCE_CEILING: Final[float] = 1.0
"""Coherence ceiling: 1.0"""


class AccessType(Enum):
    """Access result types."""

    FULL_ACCESS = auto()
    PARTIAL_ACCESS = auto()
    BLOCKED = auto()


@dataclass(frozen=True)
class AccessResult:
    """Result of access gating check."""

    type: AccessType
    alpha: float = 0.0

    @property
    def is_full_access(self) -> bool:
        """Check if result is FullAccess."""
        return self.type == AccessType.FULL_ACCESS

    @property
    def is_partial_access(self) -> bool:
        """Check if result is PartialAccess."""
        return self.type == AccessType.PARTIAL_ACCESS

    @property
    def is_blocked(self) -> bool:
        """Check if result is Blocked."""
        return self.type == AccessType.BLOCKED

    @classmethod
    def full_access(cls) -> "AccessResult":
        """Create FullAccess result."""
        return cls(AccessType.FULL_ACCESS, 1.0)

    @classmethod
    def partial_access(cls, alpha: float) -> "AccessResult":
        """Create PartialAccess result."""
        return cls(AccessType.PARTIAL_ACCESS, max(0.0, min(1.0, alpha)))

    @classmethod
    def blocked(cls) -> "AccessResult":
        """Create Blocked result."""
        return cls(AccessType.BLOCKED, 0.0)


def rac_threshold(rac: RacLevel) -> float:
    """Get threshold for a RAC level (normalized to RAC1)."""
    return rac_value_normalized(rac)


def access_level(user_coherence: float, fragment_rac: RacLevel) -> AccessResult:
    """
    Core gating function from spec Section 4.1.

    Determines access level based on user coherence and fragment RAC requirement.
    """
    threshold = rac_threshold(fragment_rac)

    if user_coherence >= threshold:
        return AccessResult.full_access()
    elif user_coherence >= COHERENCE_FLOOR:
        alpha = (user_coherence - COHERENCE_FLOOR) / (threshold - COHERENCE_FLOOR)
        return AccessResult.partial_access(alpha)
    else:
        return AccessResult.blocked()


def can_access(coherence: float, rac: RacLevel) -> bool:
    """Simple check if access is allowed (not Blocked)."""
    return not access_level(coherence, rac).is_blocked


def effective_coherence(result: AccessResult) -> float:
    """Calculate effective coherence given access result."""
    return result.alpha


def partial_emergence(current_band: Repitan, alpha: float) -> float:
    """
    Calculate partial emergence within a Repitan band.

    From spec Section 4.4.
    """
    band_low = current_band.value
    band_high = current_band.next().value
    return band_low + alpha * (band_high - band_low)


@dataclass(frozen=True)
class ResonanceWeights:
    """Weights for resonance score calculation."""

    theta: float = 0.3
    """θ alignment weight"""

    phi: float = 0.4
    """φ access weight"""

    harmonic: float = 0.2
    """h harmonic match weight"""

    radius: float = 0.1
    """r intensity weight"""


DEFAULT_WEIGHTS: Final[ResonanceWeights] = ResonanceWeights()
"""Default weights from spec Section 5.3."""


def resonance_score(
    weights: ResonanceWeights,
    theta_match: float,
    phi_access: float,
    harmonic_match: float,
    intensity: float,
) -> float:
    """
    Calculate composite resonance score.

    resonance = w_θ × θ_match + w_φ × φ_access + w_h × h_match + w_r × r_intensity
    """
    return (
        weights.theta * theta_match
        + weights.phi * phi_access
        + weights.harmonic * harmonic_match
        + weights.radius * intensity
    )


def verify_coherence_bounds() -> bool:
    """Verify Invariant R3: Coherence bounds are [0, 1]."""
    return 0 <= COHERENCE_FLOOR < 1 and COHERENCE_CEILING == 1.0


def verify_coherence_floor() -> bool:
    """Verify coherence floor calculation: φ_green / Ankh."""
    return abs(COHERENCE_FLOOR - GREEN_PHI / ANKH) < 1e-10
