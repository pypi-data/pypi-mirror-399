"""
Ra System mathematical constants - Python bindings.

This module provides type-safe access to the Ra System constants from
"The Rods of Amon Ra" by Wesley H. Bateman.

Example:
    >>> from ra_system import ANKH, Repitan, RacLevel, OmegaFormat, TON
    >>> from ra_system.gates import access_level
    >>>
    >>> # Check access at 80% coherence for RAC1
    >>> result = access_level(0.8, RacLevel.RAC1)
    >>> print(result.is_full_access)  # True
    >>>
    >>> # Create a validated Repitan
    >>> r = Repitan.create(9)
    >>> print(r.value)  # 0.333...
    >>>
    >>> # Create a T.O.N. (Table of Nines) node
    >>> t = TON.create(9)
    >>> print(t.value)  # 0.243

Invariants:
    All 17 invariants from ra_integration_spec.md are enforced:
    - Constant invariants (I1-I6)
    - Ordering invariants (O1-O4)
    - Conversion invariants (C1-C3)
    - Range invariants (R1-R4)
    - T.O.N. invariant (I5): T.O.N.(m) = m × 0.027 for all m ∈ [0, 36]
"""

from ra_system.constants import (
    ANKH,
    BLUE_PHI,
    BLUE_PI,
    FINE_STRUCTURE,
    GREEN_PHI,
    GREEN_PI,
    H_BAR,
    HUNAB,
    OMEGA,
    RED_PHI,
    RED_PI,
    AnkhValue,
    OmegaRatio,
)
from ra_system.gates import (
    COHERENCE_CEILING,
    COHERENCE_FLOOR,
    AccessResult,
    ResonanceWeights,
    access_level,
    can_access,
    effective_coherence,
    partial_emergence,
    resonance_score,
)
from ra_system.omega import (
    OmegaFormat,
    all_omega_formats,
    blue_to_red,
    convert_omega,
    green_to_omega_major,
    green_to_omega_minor,
    omega_major_to_green,
    omega_minor_to_green,
    red_to_blue,
)
from ra_system.rac import (
    RacLevel,
    RacValue,
    all_rac_levels,
    pyramid_division,
    rac_value,
    rac_value_meters,
    rac_value_normalized,
)
from ra_system.repitans import Repitan, all_repitans, repitan_from_theta
from ra_system.spherical import (
    RaCoordinate,
    coordinate_distance,
    denormalize_radius,
    normalize_radius,
    phi_from_rac,
    rac_from_phi,
    theta_from_repitan,
)
from ra_system.ton import (
    TON,
    TON_COEFFICIENT,
    all_tons,
    is_valid_ton_index,
    repitan_ton_ratio,
    ton_from_value,
    verify_ton_invariant,
    verify_ton_range_invariant,
)

__all__ = [
    # Constants
    "ANKH",
    "HUNAB",
    "H_BAR",
    "OMEGA",
    "FINE_STRUCTURE",
    "RED_PI",
    "GREEN_PI",
    "BLUE_PI",
    "RED_PHI",
    "GREEN_PHI",
    "BLUE_PHI",
    "AnkhValue",
    "OmegaRatio",
    # Repitans
    "Repitan",
    "all_repitans",
    "repitan_from_theta",
    # RAC
    "RacLevel",
    "RacValue",
    "all_rac_levels",
    "rac_value",
    "rac_value_meters",
    "rac_value_normalized",
    "pyramid_division",
    # Omega
    "OmegaFormat",
    "all_omega_formats",
    "convert_omega",
    "green_to_omega_major",
    "omega_major_to_green",
    "green_to_omega_minor",
    "omega_minor_to_green",
    "red_to_blue",
    "blue_to_red",
    # Spherical
    "RaCoordinate",
    "theta_from_repitan",
    "phi_from_rac",
    "rac_from_phi",
    "normalize_radius",
    "denormalize_radius",
    "coordinate_distance",
    # Gates
    "AccessResult",
    "COHERENCE_FLOOR",
    "COHERENCE_CEILING",
    "access_level",
    "can_access",
    "effective_coherence",
    "partial_emergence",
    "ResonanceWeights",
    "resonance_score",
    # T.O.N. (Table of Nines)
    "TON",
    "TON_COEFFICIENT",
    "all_tons",
    "is_valid_ton_index",
    "ton_from_value",
    "verify_ton_invariant",
    "verify_ton_range_invariant",
    "repitan_ton_ratio",
]

__version__ = "0.1.0"
